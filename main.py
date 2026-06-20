import os
import json
import base64
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional

from agent_engine import AgentEngine

app = FastAPI(title="AI Clone Requirements and QA Framework")

# Paths for settings and static files
SETTINGS_FILE = ".settings.json"
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

agent_engine = AgentEngine()

# Request schemas
class SettingsModel(BaseModel):
    provider: str
    apiKey: str
    model: str
    githubToken: str
    githubRepo: str
    githubBranch: str

class SimulateRequest(BaseModel):
    systemName: str
    surveyInput: str

class ReviewRequest(BaseModel):
    specText: str
    atddGherkin: str

class GitHubPushRequest(BaseModel):
    path: str
    content: str
    commitMessage: str

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Endpoints
@app.get("/")
def get_index():
    return FileResponse(os.path.join(WORKSPACE_DIR, "index.html"))

@app.get("/styles.css")
def get_css():
    return FileResponse(os.path.join(WORKSPACE_DIR, "styles.css"))

@app.get("/app.js")
def get_js():
    return FileResponse(os.path.join(WORKSPACE_DIR, "app.js"))

@app.get("/api/settings")
def api_get_settings():
    settings = load_settings()
    # Mask API key and token for safety
    masked_settings = settings.copy()
    if masked_settings.get("apiKey"):
        masked_settings["apiKey"] = masked_settings["apiKey"][:4] + "*" * (len(masked_settings["apiKey"]) - 4)
    if masked_settings.get("githubToken"):
        masked_settings["githubToken"] = masked_settings["githubToken"][:4] + "*" * (len(masked_settings["githubToken"]) - 4)
    return masked_settings

@app.post("/api/settings")
def api_save_settings(req: SettingsModel):
    # If the user saved with masked key/token, keep the existing saved values
    current = load_settings()
    new_data = req.model_dump()
    
    if "*" in new_data["apiKey"] and current.get("apiKey"):
        new_data["apiKey"] = current["apiKey"]
    if "*" in new_data["githubToken"] and current.get("githubToken"):
        new_data["githubToken"] = current["githubToken"]
        
    save_settings(new_data)
    return {"status": "success", "message": "設定を保存しました。"}

@app.post("/api/simulate")
def api_simulate(req: SimulateRequest):
    settings = load_settings()
    try:
        result = agent_engine.run_simulation(req.surveyInput, req.systemName, settings)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"シミュレーションエラー: {str(e)}")

@app.post("/api/review")
def api_review(req: ReviewRequest):
    settings = load_settings()
    try:
        result = agent_engine.run_periodic_review(req.specText, req.atddGherkin, settings)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レビューエラー: {str(e)}")

@app.post("/api/github/push")
async def api_github_push(req: GitHubPushRequest):
    settings = load_settings()
    token = settings.get("githubToken", "")
    repo = settings.get("githubRepo", "")  # Expected format: "owner/repo"
    branch = settings.get("githubBranch", "main")

    if not token or not repo:
        raise HTTPException(status_code=400, detail="GitHubのアクセストークンとリポジトリ名が設定されていません。")

    owner_repo = repo.split("/")
    if len(owner_repo) != 2:
        raise HTTPException(status_code=400, detail="リポジトリ名は 'オーナー名/リポジトリ名' の形式で入力してください。")

    owner, repo_name = owner_repo
    path = req.path.lstrip("/")

    # Build HTTP headers for GitHub API
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Clone-QA-Framework"
    }

    async with httpx.AsyncClient() as client:
        # Step 1: Check if file already exists to obtain its SHA (for update)
        file_sha = None
        get_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}?ref={branch}"
        
        try:
            get_resp = await client.get(get_url, headers=headers)
            if get_resp.status_code == 200:
                file_sha = get_resp.json().get("sha")
        except Exception as e:
            # Just ignore if checking fails; assume file is new
            pass

        # Step 2: Push the file to GitHub
        put_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
        content_bytes = req.content.encode("utf-8")
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")
        
        body = {
            "message": req.commitMessage,
            "content": content_b64,
            "branch": branch
        }
        if file_sha:
            body["sha"] = file_sha

        try:
            put_resp = await client.put(put_url, json=body, headers=headers)
            if put_resp.status_code in (200, 201):
                res_data = put_resp.json()
                html_url = res_data.get("content", {}).get("html_url", "")
                return {"status": "success", "url": html_url, "message": "GitHubへのコミットが成功しました！"}
            else:
                error_msg = put_resp.json().get("message", "不明なエラー")
                raise HTTPException(status_code=put_resp.status_code, detail=f"GitHub API エラー: {error_msg}")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"GitHubへの接続中にエラーが発生しました: {str(e)}")
