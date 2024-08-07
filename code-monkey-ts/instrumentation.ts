import { trace, Span, Tracer, context } from '@opentelemetry/api';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { BatchSpanProcessor, ConsoleSpanExporter, NodeTracerProvider } from '@opentelemetry/sdk-trace-node';

let _tracer: Tracer | null = null;

export function tracer(): Tracer {
  if (_tracer === null) {
    console.warn("WARNING: tracer not initialized. Returning NoOp tracer.");
    _tracer = trace.getTracer('replayio.ai_playground');
  }
  return _tracer;
}

export function setTracer(newTracer: Tracer): void {
  _tracer = newTracer;
}

export function currentSpan(): Span {
  return trace.getSpan(context.active()) ?? trace.getTracer('default').startSpan('');
}

export function initializeTracer(attributes?: Record<string, any>): void {
  const serviceResource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: "ai_playground",
  });

  const extraResource = attributes ? new Resource(attributes) : Resource.empty();

  let exporter: OTLPTraceExporter | ConsoleSpanExporter | null = null;
  const apiKey = process.env.HONEYCOMB_API_KEY;
  const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;

  if (apiKey && otlpEndpoint) {
    exporter = new OTLPTraceExporter({
      url: otlpEndpoint,
      headers: {
        'x-honeycomb-team': apiKey,
      },
    });
  } else if (process.env.OTEL_CONSOLE_EXPORTER) {
    exporter = new ConsoleSpanExporter();
  }

  const provider = new NodeTracerProvider({
    resource: extraResource.merge(serviceResource),
  });

  if (exporter) {
    const processor = new BatchSpanProcessor(exporter);
    provider.addSpanProcessor(processor);
  }

  provider.register();
  setTracer(trace.getTracer("replayio.ai-playground"));
}


export function instrument(name: string, params?: string[], attributes?: Record<string, any>): MethodDecorator {
  return function (
    target: any,
    propertyKey: string | symbol,
    descriptor: PropertyDescriptor
  ): PropertyDescriptor {
    const originalMethod = descriptor.value;
    descriptor.value = function (...args: any[]): any {
      const spanAttributes: Record<string, any> = {};

      if (params) {
        const includeAllKwargs = params.includes('kwargs');
        const kwargsToInclude = params
          .filter(p => p.startsWith('kwargs.'))
          .map(p => p.split('.')[1]);

        params.forEach((param, index) => {
          if (param === 'kwargs' || param.startsWith('kwargs.')) {
            return;
          }
          if (index < args.length) {
            spanAttributes[param] = args[index];
          }
        });

        const kwargs = args[args.length - 1];
        if (typeof kwargs === 'object' && kwargs !== null) {
          if (includeAllKwargs || kwargsToInclude.length > 0) {
            Object.entries(kwargs).forEach(([key, value]) => {
              if (includeAllKwargs || kwargsToInclude.includes(key)) {
                spanAttributes[`kwarg.${key}`] = value;
              }
            });
          }
        }
      }

      if (attributes) {
        Object.assign(spanAttributes, attributes);
      }

      return tracer().startActiveSpan(name, { attributes: spanAttributes }, span => {
        try {
          return originalMethod.apply(this, args);
        } finally {
          span.end();
        }
      });
    };
    return descriptor;
  };
}

export { Tracer };