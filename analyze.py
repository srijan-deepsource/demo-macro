import json
import os
import subprocess

from helper import (
    make_issue,
    prepare_result,
    publish_results,
    get_files,
)

codepath = os.environ.get("CODE_PATH", "/Users/sauravsrijan/work/macros/demo/django")
resultpath = "/tmp/results.json"
app_path = os.path.dirname(os.path.abspath(__file__))

files_to_analyze = [filename for filename in get_files(codepath) if filename.endswith(".py")]

analysis_command = [
    "semgrep",
    "--json",
    "-o",
    resultpath,
    # Load the rules config
    "-f",
    os.path.join(app_path, "django-rules")
]

def _get_issues():
    """Run the checks."""
    issues = []
    if not files_to_analyze:
        return issues

    # There are files to analyze
    subprocess.run(analysis_command + files_to_analyze)

    # Read the json, convert it into DS's format.
    with open(resultpath) as fp:
        raised_issues = json.load(fp)["results"]
    for issue in raised_issues:
        issue_code = issue["check_id"].split("::")[-1]
        issue_text = issue["extra"]["message"]
        filepath = issue["path"]
        startline = issue["start"]["line"]
        startcol = issue["start"]["col"]
        endline = issue["end"]["line"]
        endcol = issue["end"]["col"]
        issues.append(
            make_issue(
                issue_code, issue_text, filepath, startline, startcol, endline, endcol
            )
        )

    return issues

issues = _get_issues()

# Publish to DeepSource
publish_results(prepare_result(issues))
