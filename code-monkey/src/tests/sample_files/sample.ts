function greet(name: string): string {
    return `Hello, ${name}!`;
}

class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }

    subtract(a: number, b: number): number {
        return a - b;
    }
}

console.log(greet("World"));
const calc = new Calculator();
console.log(`2 + 3 = ${calc.add(2, 3)}`);
console.log(`5 - 2 = ${calc.subtract(5, 2)}`);
