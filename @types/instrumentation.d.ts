declare module 'instrumentation' {
  export function instrument(
    name: string,
    paramNames: string[],
    options?: { attributes?: Record<string, string> }
  ): (target: object, propertyKey: string, descriptor: PropertyDescriptor) => void;

  export function initializeTracer(options: { agent: string }): void;
}
