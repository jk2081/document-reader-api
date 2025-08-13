"""Admin interface for Document Reader API configuration."""

import json
import os
from typing import Dict, Any
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import config


# Create admin router
admin_router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="templates")

# Simple session storage (in production, use proper session management)
admin_sessions = set()


def create_session_id() -> str:
    """Create a simple session ID."""
    import secrets
    return secrets.token_urlsafe(32)


def verify_admin_session(request: Request) -> bool:
    """Verify admin session is valid.
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if valid session
        
    Raises:
        HTTPException: If session is invalid
    """
    session_id = request.cookies.get("admin_session")
    if not session_id or session_id not in admin_sessions:
        raise HTTPException(status_code=401, detail="Admin login required")
    return True


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file.
    
    Returns:
        Configuration dictionary
    """
    if os.path.exists(config.CONFIG_FILE):
        try:
            with open(config.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Return default config
    return {
        "api_keys": [config.API_KEY],
        "anthropic_key": config.ANTHROPIC_API_KEY,
        "settings": {
            "max_file_size": config.MAX_FILE_SIZE,
            "port": config.PORT
        }
    }


def save_config(config_data: Dict[str, Any]) -> None:
    """Save configuration to JSON file.
    
    Args:
        config_data: Configuration dictionary to save
    """
    try:
        os.makedirs(os.path.dirname(config.CONFIG_FILE), exist_ok=True)
        with open(config.CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save configuration: {str(e)}")


@admin_router.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Display admin login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@admin_router.post("/admin/login")
async def admin_login(request: Request, password: str = Form(...)):
    """Handle admin login."""
    if password == config.ADMIN_PASSWORD:
        session_id = create_session_id()
        admin_sessions.add(session_id)
        
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie("admin_session", session_id, httponly=True)
        return response
    else:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid password"}
        )


@admin_router.get("/admin/logout")
async def admin_logout(request: Request):
    """Handle admin logout."""
    session_id = request.cookies.get("admin_session")
    if session_id and session_id in admin_sessions:
        admin_sessions.remove(session_id)
    
    response = RedirectResponse(url="/admin", status_code=302)
    response.delete_cookie("admin_session")
    return response


@admin_router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _: bool = Depends(verify_admin_session)):
    """Display admin dashboard."""
    config_data = load_config()
    
    # Get basic stats
    stats = {
        "service_status": "healthy",
        "api_keys_count": len(config_data.get("api_keys", [])),
        "max_file_size_mb": config_data.get("settings", {}).get("max_file_size", 0) // (1024 * 1024)
    }
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "stats": stats, "config": config_data}
    )


@admin_router.get("/admin/keys", response_class=HTMLResponse)
async def admin_keys_page(request: Request, _: bool = Depends(verify_admin_session)):
    """Display API keys management page."""
    config_data = load_config()
    
    return templates.TemplateResponse(
        "keys.html", 
        {"request": request, "config": config_data}
    )


@admin_router.post("/admin/keys/add")
async def add_api_key(
    request: Request, 
    new_key: str = Form(...),
    _: bool = Depends(verify_admin_session)
):
    """Add a new API key."""
    try:
        config_data = load_config()
        
        if "api_keys" not in config_data:
            config_data["api_keys"] = []
        
        if new_key and new_key not in config_data["api_keys"]:
            config_data["api_keys"].append(new_key)
            save_config(config_data)
        
        return RedirectResponse(url="/admin/keys", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse(
            "keys.html", 
            {"request": request, "config": load_config(), "error": str(e)}
        )


@admin_router.post("/admin/keys/remove")
async def remove_api_key(
    request: Request,
    key_to_remove: str = Form(...),
    _: bool = Depends(verify_admin_session)
):
    """Remove an API key."""
    try:
        config_data = load_config()
        
        if "api_keys" in config_data and key_to_remove in config_data["api_keys"]:
            config_data["api_keys"].remove(key_to_remove)
            save_config(config_data)
        
        return RedirectResponse(url="/admin/keys", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse(
            "keys.html", 
            {"request": request, "config": load_config(), "error": str(e)}
        )


@admin_router.post("/admin/settings/anthropic")
async def update_anthropic_key(
    request: Request,
    anthropic_key: str = Form(...),
    _: bool = Depends(verify_admin_session)
):
    """Update Anthropic API key."""
    try:
        config_data = load_config()
        config_data["anthropic_key"] = anthropic_key
        save_config(config_data)
        
        return RedirectResponse(url="/admin/dashboard", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "config": load_config(), "error": str(e)}
        )