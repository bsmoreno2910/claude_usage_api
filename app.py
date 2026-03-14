import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Claude Usage API", version="1.0.0")

PROFILES_BASE = Path(os.getenv("PROFILES_BASE", "/data/profiles"))
CLAUDE_BIN = os.getenv("CLAUDE_BIN", "claude")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

PROFILES_BASE.mkdir(parents=True, exist_ok=True)


class UsageRequest(BaseModel):
    token: str = Field(..., min_length=10)
    profile: str = Field(default="default", min_length=1, max_length=100)


def sanitize_profile(profile: str) -> str:
    profile = profile.strip()
    profile = re.sub(r"[^a-zA-Z0-9_\-]", "_", profile)
    return profile or "default"


def run_command(cmd: list[str], env: dict) -> dict:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=REQUEST_TIMEOUT
    )
    return {
        "exit_code": result.returncode,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "success": result.returncode == 0
    }


def run_claude_usage(token: str, profile: str) -> dict:
    profile = sanitize_profile(profile)
    profile_path = PROFILES_BASE / profile
    profile_path.mkdir(parents=True, exist_ok=True)

    xdg_config_home = profile_path / ".config"
    xdg_cache_home = profile_path / ".cache"
    xdg_data_home = profile_path / ".local" / "share"

    xdg_config_home.mkdir(parents=True, exist_ok=True)
    xdg_cache_home.mkdir(parents=True, exist_ok=True)
    xdg_data_home.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = token
    env["HOME"] = str(profile_path)
    env["USERPROFILE"] = str(profile_path)
    env["XDG_CONFIG_HOME"] = str(xdg_config_home)
    env["XDG_CACHE_HOME"] = str(xdg_cache_home)
    env["XDG_DATA_HOME"] = str(xdg_data_home)

    usage_result = run_command([CLAUDE_BIN, "/usage"], env)

    return {
        "profile": profile,
        "profile_path": str(profile_path),
        **usage_result
    }


@app.get("/health")
def health():
    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "ok": result.returncode == 0,
            "claude_bin": CLAUDE_BIN,
            "version": (result.stdout or result.stderr).strip()
        }
    except Exception as ex:
        return {
            "ok": False,
            "claude_bin": CLAUDE_BIN,
            "error": str(ex)
        }


@app.post("/usage")
def usage(payload: UsageRequest, x_api_key: Optional[str] = Header(default=None)):
    expected_api_key = os.getenv("API_KEY", "").strip()
    if expected_api_key and (not x_api_key or x_api_key != expected_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        return run_claude_usage(payload.token, payload.profile)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout running claude /usage")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Claude CLI not found in container")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
