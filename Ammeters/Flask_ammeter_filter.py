from flask import Flask, render_template_string, request
import json
from datetime import datetime
import statistics

ALL_RUNS_JSON = r"../results/all_runs.json"
app = Flask(__name__)


def filter_runs(all_runs, emulator=None, start_time=None, end_time=None):
    filtered = []
    for run in all_runs:
        meta = run.get("metadata", {})
        emu_name = meta.get("emulator", "")
        run_start_str = meta.get("start_time")
        run_end_str = meta.get("end_time")
        if not run_start_str or not run_end_str:
            continue
        run_start = datetime.strptime(run_start_str, "%Y-%m-%d %H:%M:%S")
        run_end = datetime.strptime(run_end_str, "%Y-%m-%d %H:%M:%S")
        if emulator and emu_name.lower() != emulator.lower():
            continue
        if start_time and run_start < start_time:
            continue
        if end_time and run_end > end_time:
            continue
        filtered.append(run)
    return filtered


def compare_statistics(filtered_runs):
    if not filtered_runs:
        return [], {}
    comparison = []
    all_currents = []
    for run in filtered_runs:
        summary = {
            "emulator": run["metadata"].get("emulator", ""),
            "mean_current_a": run.get("mean_current_a"),
            "median_current_a": run.get("median_current_a"),
            "std_dev_current_a": run.get("std_dev_current_a"),
            "min_current_a": run.get("min_current_a"),
            "max_current_a": run.get("max_current_a"),
            "start_time": run["metadata"].get("start_time"),
            "log_file": run["metadata"].get("log_file")
        }
        comparison.append(summary)
        all_currents.append(run.get("mean_current_a"))
    overall_summary = {
        "overall_min_current_a": min(run.get("min_current_a") for run in filtered_runs),
        "overall_max_current_a": max(run.get("max_current_a") for run in filtered_runs),
        "overall_mean_current_a": statistics.mean(all_currents),
        "overall_median_current_a": statistics.median(all_currents),
        "overall_std_dev_current_a": statistics.stdev(all_currents) if len(all_currents) > 1 else 0
    }
    return comparison, overall_summary


# Bootstrap template
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ammeter Runs Summary</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
    <h1 class="mb-4">Ammeter Runs Summary</h1>

    <div class="card mb-4">
        <div class="card-header">
            <strong>Filter Runs</strong>
        </div>
        <div class="card-body">
            <form method="POST" class="row g-3">
                <div class="col-md-4">
                    <label for="emulator" class="form-label">Emulator</label>
                    <select class="form-select" id="emulator" name="emulator">
                        <option value="">-- All --</option>
                        <option value="Greenlee">Greenlee</option>
                        <option value="Entes">Entes</option>
                        <option value="Circutor">Circutor</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label for="start_time" class="form-label">Start time</label>
                    <input type="datetime-local" class="form-control" id="start_time" name="start_time">
                </div>
                <div class="col-md-4">
                    <label for="end_time" class="form-label">End time</label>
                    <input type="datetime-local" class="form-control" id="end_time" name="end_time">
                </div>
                <div class="col-12">
                    <button type="submit" class="btn btn-primary mt-2">Filter</button>
                </div>
            </form>
        </div>
    </div>

    {% if overall_summary %}
    <div class="card">
        <div class="card-header">
            <strong>Overall Summary</strong>
        </div>
        <div class="card-body">
            <ul class="list-group list-group-flush">
                {% for key, value in overall_summary.items() %}
                <li class="list-group-item"><strong>{{ key.replace('_', ' ').title() }}:</strong> {{ value }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    {% elif comparison %}
    <div class="card">
        <div class="card-header">
            <strong>Filter Summary</strong>
        </div>
        <div class="card-body">
            <ul class="list-group list-group-flush">
                <li class="list-group-item"><strong>Emulator:</strong> {{ emulator_selected if emulator_selected else "All" }}</li>
                <li class="list-group-item"><strong>Number of Runs:</strong> {{ comparison|length }}</li>
            </ul>
        </div>
    </div>
    {% endif %}
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    overall_summary = None
    comparison = []

    # Load all runs
    with open(ALL_RUNS_JSON, "r") as f:
        all_runs = json.load(f)

    if request.method == "POST":
        emulator = request.form.get("emulator")
        start_str = request.form.get("start_time")
        end_str = request.form.get("end_time")
        # Handle datetime-local input
        start_time = datetime.strptime(start_str, "%Y-%m-%dT%H:%M") if start_str else None
        end_time = datetime.strptime(end_str, "%Y-%m-%dT%H:%M") if end_str else None
        filtered_runs = filter_runs(all_runs, emulator=emulator, start_time=start_time, end_time=end_time)
        comparison, overall_summary = compare_statistics(filtered_runs)
        
        # Add number of measurements and emulator name to overall_summary
        if overall_summary:
            total_measurements = sum(run.get("total_measurements", 0) for run in filtered_runs)
            overall_summary["total_measurements"] = total_measurements
            overall_summary["emulator_name"] = emulator if emulator else "All"

    return render_template_string(TEMPLATE, comparison=comparison, overall_summary=overall_summary, 
                                 emulator_selected=emulator if request.method == "POST" else None)


if __name__ == "__main__":
    app.run(debug=True)
