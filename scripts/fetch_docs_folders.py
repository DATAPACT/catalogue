import base64
import os
from pathlib import Path

import requests
import yaml

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

def save_file(base_dir, repo, file_path, content_bytes):
    rel_path = Path(file_path)
    out_path = base_dir / repo / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("wb") as f:
        f.write(content_bytes)

    print(f"[OK] Saved {out_path}")

    # Generate README.html using local Markdown rendering
    if rel_path.name.lower() == "readme.md":
        print(f"[INFO] Rendering {repo}/{file_path} -> README.html...")
        try:
            import markdown

            md_text = content_bytes.decode("utf-8")

            # Convert Markdown to embeddable HTML fragment
            md_html = markdown.markdown(
                md_text,
                extensions=["tables", "fenced_code", "attr_list"]
            )

            html_path = out_path.with_suffix(".html")
            with html_path.open("w", encoding="utf-8") as f:
                f.write(md_html)

            print(f"[OK] Saved {html_path}")

        except Exception as e:
            print(f"[WARN] HTML render error: {e}")

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
