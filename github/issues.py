import json
import subprocess


def get_issue(repo, issue_number):
    """Fetch issue details using GitHub CLI"""
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), "--repo", repo, "--json",
         "title,body,labels,comments"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)