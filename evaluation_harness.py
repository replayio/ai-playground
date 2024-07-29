import json
import os

def load_problems(problem_file):
    with open(problem_file, 'r') as f:
        problems = json.load(f)
    return problems

def run_model(model, problem):
    # Placeholder for model execution
    # Replace with actual model inference code
    return model(problem['input'])

def compare_outputs(model_output, expected_output):
    return model_output == expected_output

def record_results(results, output_file):
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

def summarize_results(results):
    total = len(results)
    correct = sum(1 for result in results if result['correct'])
    accuracy = correct / total if total > 0 else 0
    print(f"Total problems: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")

def main():
    problem_file = 'human_eval_problems.json'
    output_file = 'evaluation_results.json'
    model = lambda x: x  # Placeholder for the actual model

    problems = load_problems(problem_file)
    results = []

    for problem in problems:
        model_output = run_model(model, problem)
        correct = compare_outputs(model_output, problem['output'])
        results.append({
            'problem_id': problem['id'],
            'input': problem['input'],
            'expected_output': problem['output'],
            'model_output': model_output,
            'correct': correct
        })

    record_results(results, output_file)
    summarize_results(results)

if __name__ == "__main__":
    main()
