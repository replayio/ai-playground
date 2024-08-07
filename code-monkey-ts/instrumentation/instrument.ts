export function instrument(
  name: string,
  paramNames: string[],
  options?: { attributes?: Record<string, string> }
): ClassDecorator & MethodDecorator {
  return function(
    target: any,
    propertyKey?: string | symbol,
    descriptor?: PropertyDescriptor
  ): any {
    if (descriptor) {
      // Method decorator
      const originalMethod = descriptor.value;
      descriptor.value = function(this: unknown, ...args: unknown[]) {
        console.log(`Instrumenting ${name} with params: ${paramNames.join(', ')}`);
        if (options?.attributes) {
          console.log(`Attributes: ${JSON.stringify(options.attributes)}`);
        }
        return originalMethod.apply(this, args);
      };
      return descriptor;
    } else {
      // Class decorator
      console.log(`Instrumenting class ${name}`);
      if (options?.attributes) {
        console.log(`Attributes: ${JSON.stringify(options.attributes)}`);
      }
      return target;
    }
  };
}

export function instrumentMethod<T extends (...args: unknown[]) => unknown>(
  name: string,
  paramNames: string[],
  options?: { attributes?: Record<string, string> }
): (target: object, propertyKey: string, descriptor: TypedPropertyDescriptor<T>) => TypedPropertyDescriptor<T> {
  return function(
    target: object,
    propertyKey: string,
    descriptor: TypedPropertyDescriptor<T>
  ): TypedPropertyDescriptor<T> {
    const originalMethod = descriptor.value;
    if (originalMethod) {
      descriptor.value = function(this: unknown, ...args: unknown[]) {
        console.log(`Instrumenting ${name} with params: ${paramNames.join(', ')}`);
        if (options?.attributes) {
          console.log(`Attributes: ${JSON.stringify(options.attributes)}`);
        }
        return originalMethod.apply(this, args);
      } as T;
    }
    return descriptor;
  };
}

export function instrumentFunction<T extends (...args: unknown[]) => unknown>(
  name: string,
  paramNames: string[],
  options?: { attributes?: Record<string, string> }
): (func: T) => T {
  return function(func: T): T {
    return function(this: unknown, ...args: unknown[]) {
      console.log(`Instrumenting ${name} with params: ${paramNames.join(', ')}`);
      if (options?.attributes) {
        console.log(`Attributes: ${JSON.stringify(options.attributes)}`);
      }
      return func.apply(this, args);
    } as T;
  };
}
