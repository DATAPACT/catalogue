import base64
import os
from pathlib import Path

import requests
import yaml
import json  # ← NEW: for API responses

CONFIG_PATH = Path("config/tools.yml")
OUTPUT_DIR = Path("output")

def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def github_get_tree(org, repo, path, ref, token):
    url = f"https://api.github.com/repos/{org}/{repo}/git/trees/{ref}:{path}?recursive=1"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print(f"[WARN] {org}/{repo}:{path}@{ref} not found")
        return []
    resp.raise_for_status()
    return resp.json().get("tree", [])

def github_get_file_content(org, repo, file_sha, token):
    url = f"https://api.github.com/repos/{org}/{repo}/git/blobs/{file_sha}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    content = data.get("content", "")
    encoding = data.get("encoding", "base64")
    if encoding == "base64":
        return base64.b64decode(content)
    return content.encode("utf-8")

# ← NEW: GitHub's public Markdown→HTML API (no install needed)
def github_render_markdown(org, repo, branch, file_path, token):
    url = "https://api.github.com/markdown"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "text": "",
        "mode": "markdown", 
        "context": f"{org}/{repo}"
    }
    
    # Get raw README.md content
    tree = github_get_tree(org, repo, "", branch, token)
    readme_blob = next((i for i in tree if i["path"].lower() == file_path.lower()), None)
    if not readme_blob:
        return None
        
    content_bytes = github_get_file_content(org, repo, readme_blob["sha"], token)
    data["text"] = content_bytes.decode("utf-8", errors="replace")
    
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        print(f"[WARN] Markdown render failed: {resp.status_code}")
        return None
    return resp.content

def save_file(base_dir, repo, file_path, content_bytes):
    rel_path = Path(file_path)
    out_path = base_dir / repo / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(content_bytes)
    print(f"[OK] Saved {out_path}")

    # ← NEW: Auto-generate README.html from README.md using GitHub API
    if rel_path.name.lower() == "readme.md":
        print(f"[INFO] Rendering {repo}/{file_path} → README.html...")
        token = os.environ["GITHUB_PAT"]
        org = os.environ["GITHUB_ORG"]
        branch = "main"  # assumes main branch (adjust if needed)
        
        html_content = github_render_markdown(org, repo, branch, file_path, token)
        if html_content:
            html_path = out_path.with_suffix(".html")
            with html_path.open("wb") as f:
                f.write(html_content)
            print(f"[OK] Saved {html_path}")
        else:
            print(f"[WARN] HTML render failed for {repo}/{file_path}")

def main():
    token = os.environ["GITHUB_PAT"]
    org = os.environ["GITHUB_ORG"]
    
    cfg = load_config()
    tools = cfg.get("tools", [])
    print(f"[CRITICAL DEBUG] FULL TOOLS LIST ({len(tools)}): {[t['repo'] for t in tools]}")  
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    for tool in tools:
        repo = tool["repo"]
        branch = tool.get("branch", "main")
        docs_root = tool.get("docs_root", "")
        
        if docs_root:
            print(f"\n=== Fetching {org}/{repo}/{docs_root}@{branch} ===")
            tree_items = github_get_tree(org, repo, docs_root, branch, token)

            print(f"[DEBUG] {org}/{repo}/{docs_root}@{branch}: {len(tree_items)} items")
            if not tree_items:
                print(f"[DEBUG] EMPTY - check https://github.com/{org}/{repo}/tree/{branch}/{docs_root}")
            
            for item in tree_items:
                if item["type"] == "blob":
                    content = github_get_file_content(org, repo, item["sha"], token)
                    if content:
                        save_file(OUTPUT_DIR, repo, item["path"], content)

if __name__ == "__main__":
    main()
