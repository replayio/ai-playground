// @ts-expect-error Type definitions for @opentelemetry/api may be incomplete or incompatible
import { Span, SpanStatusCode, trace } from '@opentelemetry/api';

const tracer = trace.getTracer('agent');

export function instrument(name: string, attributes: string[] = []) {
    return function (target: unknown, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;

        descriptor.value = function (...args: unknown[]) {
            return tracer.startActiveSpan(name, (span: Span) => {
                try {
                    attributes.forEach((attr, index) => {
                        if (index < args.length) {
                            span.setAttribute(attr, JSON.stringify(args[index]));
                        }
                    });

                    const result = originalMethod.apply(this, args);

                    if (result instanceof Promise) {
                        return result.then(
                            (res) => {
                                span.setStatus({ code: SpanStatusCode.OK });
                                span.end();
                                return res;
                            },
                            (err: Error) => {
                                span.setStatus({
                                    code: SpanStatusCode.ERROR,
                                    message: err.message,
                                });
                                span.recordException(err);
                                span.end();
                                throw err;
                            }
                        );
                    } else {
                        span.setStatus({ code: SpanStatusCode.OK });
                        span.end();
                        return result;
                    }
                } catch (error: unknown) {
                    if (error instanceof Error) {
                        span.setStatus({
                            code: SpanStatusCode.ERROR,
                            message: error.message,
                        });
                        span.recordException(error);
                    } else {
                        span.setStatus({
                            code: SpanStatusCode.ERROR,
                            message: 'An unknown error occurred',
                        });
                    }
                    span.end();
                    throw error;
                }
            });
        };

        return descriptor;
    };
}

export function currentSpan(): Span {
    return trace.getActiveSpan() || trace.getTracer('agent').startSpan('default');
}
