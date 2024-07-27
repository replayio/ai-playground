function greet(name) {
    return `Hello, ${name}!`;
}

class Calculator {
    add(a, b) {
        return a + b;
    }

    subtract(a, b) {
        return a - b;
    }
}

console.log(greet("World"));
const calc = new Calculator();
console.log(`2 + 3 = ${calc.add(2, 3)}`);
console.log(`5 - 2 = ${calc.subtract(5, 2)}`);
