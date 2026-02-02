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
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+js
