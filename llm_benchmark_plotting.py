from pathlib import Path

import matplotlib.pyplot as plt
import json
import os
import glob

# File paths for the results of the two models
current_dir = Path(__file__).parent

model_results = {
    "Model 1": sorted(
        (current_dir / "benchmarks/model_1/").glob("*/"),
        key=os.path.getctime, reverse=True
    )[0],  # Selects the latest matching directory
    "Model 2": sorted(
        (current_dir / "benchmarks/model_2/").glob("*/"),
        key=os.path.getctime, reverse=True
    )[0]  # Selects the latest matching directory
}

metrics = {model: {} for model in model_results}
tasks = set()

# Extract metrics from JSON files
for model, dir_path in model_results.items():
    result_files = glob.glob(os.path.join(dir_path, "results_*.json"))
    if result_files:
        latest_file = max(result_files, key=os.path.getctime)
        with open(latest_file) as f:
            data = json.load(f)
            for task, task_metrics in data['results'].items():
                tasks.add(task)
                metrics[model][task] = task_metrics

for task in sorted(tasks):
    plt.figure(figsize=(12, 7))
    plt.title(f'{task} Comparison: Model 1 vs Model 2')

    model_metrics = [metrics[m].get(task, {}) for m in model_results]
    shared_metrics = set(model_metrics[0].keys()) & set(model_metrics[1].keys())

    # Ensure GSM8K plots correctly by using specific known keys
    if task == "gsm8k":
        shared_metrics = {"exact_match,strict-match", "exact_match,flexible-extract"}

    metric_names = sorted({m.split(',')[0] for m in shared_metrics})

    if not metric_names:
        plt.close()
        continue

    x = range(len(metric_names))
    width = 0.35

    for i, model in enumerate(model_results):
        values = [metrics[model].get(task, {}).get(f'{metric},strict-match',
                 metrics[model].get(task, {}).get(f'{metric},none', 0)) for metric in metric_names]

        errors = [metrics[model].get(task, {}).get(f'{metric}_stderr,strict-match',
                  metrics[model].get(task, {}).get(f'{metric}_stderr,none', 0)) for metric in metric_names]

        bars = plt.bar([p + i * width for p in x], values, width, yerr=errors, capsize=5, label=model)

        # Show values below the bars
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() - 0.02,
                     f'{value:.5f}', ha='center', va='top', fontsize=8, fontweight='bold')

    plt.axhline(0, color='grey', linestyle='--')
    plt.xticks([p + width / 2 for p in x], metric_names, rotation=45, ha="right")
    plt.ylabel('Scores')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    output_path = current_dir /  f'benchmarks/{task}_comparison.png'
    plt.savefig(output_path)
    print(f"Generated comparison plot for {task} at {output_path}")
    plt.close()
