import functools
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, Attributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

# re-export this from here so we don't have to litter the code with otel imports
Tracer = trace.Tracer

_tracer = None

def tracer() -> Tracer:
    global _tracer
    return _tracer

def set_tracer(tracer: Tracer):
    global _tracer
    _tracer = tracer

def current_span() -> trace.Span:
    return trace.get_current_span()

# Creates a tracer from the global tracer provider
def initialize_tracer(attributes: Attributes = None):
    service_resource = Resource.create({
        SERVICE_NAME: "ai_playground",
    })

    extra_resource = Resource.get_empty() if attributes is None else Resource.create(attributes)

    exporter = None
    if os.getenv("HONEYCOMB_API_KEY") is not None and os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") is not None:
        # TODO(toshok): this is for grpc, which I'd love to use, but doesn't seem to work?
        # exporter = OTLPSpanExporter(
        #     endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        #     headers=(("x-honeycomb-team", os.getenv("HONEYCOMB_API_KEY"))),
        # )
        exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers={
                "x-honeycomb-team": os.getenv("HONEYCOMB_API_KEY"),
            },
        )
    elif os.getenv("OTEL_CONSOLE_EXPORTER"):
        exporter = ConsoleSpanExporter()

    if exporter is None:
        provider = trace.NoOpTracerProvider()
    else:
        provider = TracerProvider(
            resource=extra_resource.merge(service_resource)
        )
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

    # Sets the global default tracer provider
    trace.set_tracer_provider(provider)

    set_tracer(trace.get_tracer("replayio.ai-playground"))


def instrument(name: str, attributes=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tracer().start_as_current_span(name, attributes=attributes):
                return func(*args, **kwargs)
        return wrapper
    return decorator