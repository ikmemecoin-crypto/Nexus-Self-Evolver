import os
import sys
import asyncio
import logging
import threading
import platform
import psutil
import aiohttp
import aiosqlite
import httpx
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bleach import clean
from cryptography.fernet import Fernet
from scapy.all import sniff, IP
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv

# 1. Initialization & Security
load_dotenv()
app = FastAPI(title="SOVEREIGN_GOD_TIER_V1", version="2026.02.15")
templates = Jinja2Templates(directory="templates")

# Master Encryption Key for the Omniscience Vault
SECRET_KEY = os.getenv("SOVEREIGN_KEY", Fernet.generate_key())
cipher_suite = Fernet(SECRET_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sovereign_core")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- CORE MODULES ---

class SystemGovernor:
    """Manages physical laptop resources."""
    @staticmethod
    def get_health():
        return {
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "ram_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "disk_free": f"{psutil.disk_usage('/').free / (1024**3):.2f} GB",
            "os": platform.system()
        }
    
    @staticmethod
    async def optimize():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in ['UpdateAgent', 'TempSync']: # Example targets
                proc.terminate()
        logger.info("System Resources Optimized.")

class IntelligenceVault:
    """Encrypted persistent memory."""
    async def init_db(self):
        async with aiosqlite.connect("omniscience.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS vault (id INTEGER PRIMARY KEY, topic TEXT, data TEXT)")
            await db.commit()

    async def secure_store(self, topic: str, content: str):
        encrypted = cipher_suite.encrypt(content.encode()).decode()
        async with aiosqlite.connect("omniscience.db") as db:
            await db.execute("INSERT INTO vault (topic, data) VALUES (?, ?)", (topic, encrypted))
            await db.commit()

class GuardianShield:
    """Intrusion detection and Kill-Switch."""
    def __init__(self):
        self.authorized_ips = ["127.0.0.1"]
    
    def sentinel(self, packet):
        if packet.haslayer(IP) and packet[IP].src not in self.authorized_ips:
            if packet[IP].dport in [8000, 22]:
                logger.critical("UNAUTHORIZED ACCESS. EXECUTING KILL-SWITCH.")
                os._exit(1)

    def start(self):
        t = threading.Thread(target=lambda: sniff(prn=self.sentinel, store=0))
        t.daemon = True
        t.start()

# --- INITIALIZATION ---
governor = SystemGovernor()
vault = IntelligenceVault()
shield = GuardianShield()

class IntentRequest(BaseModel):
    intent: str

@app.on_event("startup")
async def startup():
    await vault.init_db()
    shield.start()
    logger.info("SOVEREIGN ENTITY ASCENDED.")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/system/status")
async def status():
    return {"health": governor.get_health(), "status": "Online"}

@app.post("/execute")
async def execute(request: IntentRequest, background_tasks: BackgroundTasks):
    sanitized = clean(request.intent)
    if "secure" in sanitized.lower():
        background_tasks.add_task(governor.optimize)
    return {"status": "Executing", "intent": sanitized}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
