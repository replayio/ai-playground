import * as os from "node:os";
import {
  trace,
  Span,
  Tracer,
  context as otelContext,
  SpanStatusCode,
  Attributes,
  Baggage,
  propagation,
  BaggageEntry,
} from "@opentelemetry/api";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { Resource } from "@opentelemetry/resources";
import {
  SEMRESATTRS_HOST_ARCH,
  SEMRESATTRS_OS_NAME,
  SEMRESATTRS_OS_TYPE,
  SEMRESATTRS_OS_VERSION,
  SEMRESATTRS_PROCESS_RUNTIME_NAME,
  SEMRESATTRS_PROCESS_RUNTIME_VERSION,
  SEMRESATTRS_SERVICE_NAME,
} from "@opentelemetry/semantic-conventions";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import {
  BatchSpanProcessor,
  ConsoleSpanExporter,
  NodeTracerProvider,
} from "@opentelemetry/sdk-trace-node";

let _provider: NodeTracerProvider | null = null;
let _tracer: Tracer | null = null;

export function tracer(): Tracer {
  if (_tracer === null) {
    console.warn("WARNING: tracer not initialized. Returning NoOp tracer.");
    _tracer = trace.getTracer("replayio.ai_playground");
  }
  return _tracer;
}

export function setTracer(newTracer: Tracer): void {
  _tracer = newTracer;
}

export function currentSpan(): Span {
  return (
    trace.getSpan(otelContext.active()) ??
    trace.getTracer("default").startSpan("")
  );
}

export function currentBaggage(): Baggage | undefined {
  return propagation.getActiveBaggage();
}

export function withKVBaggage<T extends () => any>(
  kvs: Attributes,
  fn: T,
): ReturnType<T> {
  const baggageEntries: Record<string, BaggageEntry> = {};
  Object.entries(kvs).forEach(([key, value]) => {
    baggageEntries[key] = { value: String(value) };
  });

  let baggage = currentBaggage();
  if (baggage) {
    Object.entries(baggageEntries).forEach(([key, entry]) => {
      baggage = baggage!.setEntry(key, entry);
    });
  } else {
    baggage = propagation.createBaggage(baggageEntries);
  }

  return otelContext.with(
    propagation.setBaggage(otelContext.active(), baggage),
    fn,
  );
}

export function initializeTracer(attributes?: Record<string, any>): void {
  const serviceResources = new Resource({
    [SEMRESATTRS_SERVICE_NAME]: "ai_playground",
    [SEMRESATTRS_HOST_ARCH]: process.arch,
    [SEMRESATTRS_OS_TYPE]: process.platform,
    [SEMRESATTRS_OS_NAME]: os.type(),
    [SEMRESATTRS_OS_VERSION]: os.version(),
    [SEMRESATTRS_PROCESS_RUNTIME_NAME]: "nodejs",
    [SEMRESATTRS_PROCESS_RUNTIME_VERSION]: process.version,
    ["user.username"]: os.userInfo().username,
  });

  const extraResource = attributes
    ? new Resource(attributes)
    : Resource.empty();

  let exporter: OTLPTraceExporter | ConsoleSpanExporter | null = null;
  const apiKey = process.env.HONEYCOMB_API_KEY;
  const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;

  if (apiKey && otlpEndpoint) {
    exporter = new OTLPTraceExporter({
      url: otlpEndpoint,
      headers: {
        "x-honeycomb-team": apiKey,
      },
    });
  } else if (process.env.OTEL_CONSOLE_EXPORTER) {
    exporter = new ConsoleSpanExporter();
  }

  _provider = new NodeTracerProvider({
    resource: extraResource.merge(serviceResources),
  });

  if (exporter) {
    const processor = new BatchSpanProcessor(exporter);
    _provider.addSpanProcessor(processor);
  }

  _provider.register();

  registerInstrumentations({
    instrumentations: [new HttpInstrumentation()],
  });
  setTracer(trace.getTracer("replayio.ai-playground"));
}

export async function shutdownTracer(): Promise<void> {
  if (_provider) {
    try {
      await _provider.forceFlush();
    } catch (e) {
      console.error("Error flushing spans:", e);
    }

    try {
      await _provider.shutdown();
    } catch (e) {
      console.error("Error shutting down tracer:", e);
    }

    // TODO(toshok) more to do here?
    _provider = null;
    _tracer = null;
  }
}

type InstrumentOptions = {
  attributes?: Attributes;
  excludeBaggage?: boolean;
};

export function instrument<T extends (...args: any) => any>(
  name: string,
  options?: InstrumentOptions,
) {
  return function (originalMethod: T, context: DecoratorContext) {
    if (context.kind === "method") {
      return function (...args: Parameters<T>): ReturnType<T> {
        const attributes: Attributes = {};

        if (!options?.excludeBaggage) {
          const parentContext = otelContext.active();
          if (parentContext) {
            (
              propagation.getBaggage(parentContext)?.getAllEntries() ?? []
            ).forEach(([key, { value }]) => {
              attributes[key] = value;
            });
          }
        }

        if (options?.attributes) {
          Object.assign(attributes, options.attributes);
        }

        return tracer().startActiveSpan(
          name,
          { attributes },
          (span: Span): ReturnType<T> => {
            let rv: ReturnType<T>;
            try {
              rv = originalMethod.apply(this, args);
            } catch (e) {
              span.recordException(e);
              span.setStatus({
                code: SpanStatusCode.ERROR,
                message: e.message,
              });
              span.end();
              throw e;
            }

            if ((rv as any) instanceof Promise) {
              return rv.then(
                (result: ReturnType<T>) => {
                  span.end();
                  return result;
                },
                (error: any) => {
                  span.recordException(error);
                  span.setStatus({
                    code: SpanStatusCode.ERROR,
                    message: error.message,
                  });
                  span.end();
                  throw error;
                },
              );
            }

            span.end();
            return rv;
          },
        );
      };
    }

    throw new Error(
      `instrument decorator only supports kind='method': kind=${context.kind}`,
    );
  };
}

export { Tracer };
