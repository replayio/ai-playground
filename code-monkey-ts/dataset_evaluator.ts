import fetch from 'node-fetch';

interface Problem {
    id: number;
    input: string;
    output: string;
}

async function fetchDataset(url: string): Promise<Problem[]> {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch dataset: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
}

function evaluateProblem(problem: Problem, model: (input: string) => string): boolean {
    const modelOutput = model(problem.input);
    return modelOutput === problem.output;
}

function evaluateDataset(problems: Problem[], model: (input: string) => string): { total: number, correct: number, accuracy: number } {
    let correct = 0;
    for (const problem of problems) {
        if (evaluateProblem(problem, model)) {
            correct++;
        }
    }
    const total = problems.length;
    const accuracy = total > 0 ? (correct / total) * 100 : 0;
    return { total, correct, accuracy };
}

async function main() {
    const datasetUrl = 'https://huggingface.co/datasets/THUDM/humaneval-x/viewer';
    try {
        const problems = await fetchDataset(datasetUrl);
        const model = (input: string) => input; // Placeholder model function
        const results = evaluateDataset(problems, model);
        console.log(`Total problems: ${results.total}`);
        console.log(`Correct: ${results.correct}`);
        console.log(`Accuracy: ${results.accuracy.toFixed(2)}%`);
    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}

main();
