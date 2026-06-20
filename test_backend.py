import os
import json
import pytest
from fastapi.testclient import TestClient
from main import app, SETTINGS_FILE

@pytest.fixture
def client():
    # Setup: ensure settings file is clear or backed up if needed
    backup = None
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            backup = f.read()
        os.remove(SETTINGS_FILE)
        
    yield TestClient(app)
    
    # Teardown: restore backup settings
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)
    if backup is not None:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write(backup)

def test_static_routes(client):
    """Test that static index, styles, and scripts load correctly."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AI-Clone QA" in resp.text
    
    resp = client.get("/styles.css")
    assert resp.status_code == 200
    assert "app-container" in resp.text
    
    resp = client.get("/app.js")
    assert resp.status_code == 200
    assert "DOMContentLoaded" in resp.text

def test_settings_endpoints(client):
    """Test getting and saving settings."""
    # Should start empty or default
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {}
    
    # Update settings
    payload = {
        "provider": "gemini",
        "apiKey": "test-gemini-key",
        "model": "gemini-2.5-flash",
        "githubToken": "test-github-token",
        "githubRepo": "testowner/testrepo",
        "githubBranch": "develop"
    }
    resp = client.post("/api/settings", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    
    # Get settings again, keys should be masked
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "gemini"
    assert data["apiKey"].startswith("test")
    assert "*" in data["apiKey"]
    assert data["githubToken"].startswith("test")
    assert "*" in data["githubToken"]
    assert data["githubRepo"] == "testowner/testrepo"
    assert data["githubBranch"] == "develop"

def test_simulate_mock_endpoint(client):
    """Test simulation trigger in default mock mode."""
    payload = {
        "systemName": "経費承認モバイル",
        "surveyInput": "スマホからアップロードした領収書を正しく認識してほしい。勘定科目も自動で割り当ててほしい。"
    }
    resp = client.post("/api/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["domain"] == "expense"
    assert len(data["user_clones"]) > 0
    assert len(data["duplicate_clones"]) > 0
    assert len(data["debate_logs"]) > 0
    assert "Feature:" in data["atdd_gherkin"]
    assert "test" in data["playwright_code"]
    assert "usability" in data["quality_metrics"]
    assert "director_summary" in data

def test_review_mock_endpoint(client):
    """Test periodic specifications review."""
    payload = {
        "specText": "経費精算設計書: ユーザーが領収書画像をアップロードするとOCR解析され、推奨の勘定科目をTop3件表示する。",
        "atddGherkin": "Feature: 経費精算の領収書アップロード\nScenario: アップロードと自動仕訳の確認\nGiven ...\nWhen ...\nThen ..."
    }
    resp = client.post("/api/review", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    
    assert "score" in data
    assert "status" in data
    assert "details" in data
    assert data["score"] >= 80
