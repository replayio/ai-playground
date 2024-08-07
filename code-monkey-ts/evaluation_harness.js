const fs = require('fs');

function loadProblems(problemFile) {
    const data = fs.readFileSync(problemFile, 'utf8');
    return JSON.parse(data);
}

function runModel(model, problem) {
    // Placeholder for model execution
    // Replace with actual model inference code
    return model(problem.input);
}

function compareOutputs(modelOutput, expectedOutput) {
    return modelOutput === expectedOutput;
}

function recordResults(results, outputFile) {
    fs.writeFileSync(outputFile, JSON.stringify(results, null, 4));
}

function summarizeResults(results) {
    const total = results.length;
    const correct = results.filter(result => result.correct).length;
    const accuracy = total > 0 ? (correct / total) * 100 : 0;
    console.log(`Total problems: ${total}`);
    console.log(`Correct: ${correct}`);
    console.log(`Accuracy: ${accuracy.toFixed(2)}%`);
}

function main() {
    const problemFile = 'human_eval_problems.json';
    const outputFile = 'evaluation_results.json';
    const model = input => input;  // Placeholder for the actual model

    const problems = loadProblems(problemFile);
    const results = problems.map(problem => {
        const modelOutput = runModel(model, problem);
        const correct = compareOutputs(modelOutput, problem.output);
        return {
            problem_id: problem.id,
            input: problem.input,
            expected_output: problem.output,
            model_output: modelOutput,
            correct: correct
        };
    });

    recordResults(results, outputFile);
    summarizeResults(results);
}

main();
