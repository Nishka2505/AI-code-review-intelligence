# src/data_collector.py
import os, time, pandas as pd
from github import Github
from dotenv import load_dotenv

load_dotenv()
g = Github(os.getenv("GITHUB_TOKEN"))

REPOS = [
    "microsoft/vscode",
    "facebook/react",
    "kubernetes/kubernetes"
]

def is_bug_fix(pr):
    labels = [l.name.lower() for l in pr.labels]
    title = pr.title.lower()
    keywords = ['bug','fix','crash','error','issue','defect','regression']
    return any(k in labels or k in title for k in keywords)

def collect_prs(repo_name, max_prs=300):
    repo = g.get_repo(repo_name)
    records = []
    for pr in repo.get_pulls(state='closed', sort='updated', direction='desc'):
        if len(records) >= max_prs:
            break
        if not pr.merged_at:
            continue
        try:
            reviews = list(pr.get_reviews())
            files = list(pr.get_files())
            records.append({
                'pr_number': pr.number, 'title': pr.title,
                'body': (pr.body or '')[:500],
                'additions': pr.additions, 'deletions': pr.deletions,
                'changed_files': pr.changed_files, 'commits': pr.commits,
                'comments': pr.comments, 'review_comments': pr.review_comments,
                'num_reviewers': len(set(r.user.login for r in reviews if r.user)),
                'author': pr.user.login if pr.user else 'unknown',
                'reviewers': str([r.user.login for r in reviews if r.user]),
                'files_changed': str([f.filename for f in files]),
                'diff_patch': ' '.join([f.patch or '' for f in files])[:3000],
                'is_bug_fix': int(is_bug_fix(pr)),
                'created_at': pr.created_at, 'merged_at': pr.merged_at,
                'repo': repo_name
            })
            time.sleep(0.8)
        except:
            continue
    return records

if __name__ == "__main__":
    all_records = []
    for repo in REPOS:
        all_records.extend(collect_prs(repo))
    pd.DataFrame(all_records).to_csv('data/raw/pr_data.csv', index=False)
    print(f"Saved {len(all_records)} PRs")