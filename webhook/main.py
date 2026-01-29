"""Telegram Webhook Listener for AgentFICO Contract Events."""

import json
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from web3 import Web3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgentFICO Webhook Listener",
    description="Listens for contract events and sends Telegram notifications",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
CONTRACT_ADDRESS = os.getenv("AGENTFICO_CONTRACT", "0xdF7699A597662330E553C0f48CEb16ace8b339C6")

# Risk level names
RISK_LEVEL_NAMES = {
    1: "Excellent",
    2: "Good",
    3: "Average",
    4: "Below Average",
    5: "Poor",
}


async def send_telegram_message(message: str) -> bool:
    """Send a message to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured")
        return False

    try:
        async with AsyncClient() as client:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            }
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "bot_connected": bool(TELEGRAM_BOT_TOKEN),
    }


@app.post("/webhook/score-updated")
async def on_score_updated(event: dict):
    """Webhook for ScoreUpdated events from AgentFICO contract.
    
    Expected format:
    {
        "agent": "0x...",
        "overall": 336,
        "riskLevel": 1,
        "antiGamingApplied": true,
        "updatedBy": "0x...",
        "timestamp": "2026-01-29T15:00:00Z"
    }
    """
    try:
        agent = event.get("agent", "unknown")
        overall = event.get("overall", 0)
        risk_level = event.get("riskLevel", 0)
        anti_gaming = event.get("antiGamingApplied", False)
        updated_by = event.get("updatedBy", "unknown")
        timestamp = event.get("timestamp", datetime.utcnow().isoformat())

        risk_name = RISK_LEVEL_NAMES.get(risk_level, "Unknown")
        gaming_status = "✅ Applied" if anti_gaming else "❌ Not Applied"

        message = (
            f"<b>📊 Agent Score Updated</b>\n\n"
            f"<b>Agent:</b> <code>{agent[:10]}...{agent[-4:]}</code>\n"
            f"<b>Overall Score:</b> <code>{overall}</code>\n"
            f"<b>Risk Level:</b> {risk_name}\n"
            f"<b>Anti-Gaming:</b> {gaming_status}\n"
            f"<b>Updated By:</b> <code>{updated_by[:10]}...{updated_by[-4:]}</code>\n"
            f"<b>Time:</b> {timestamp}\n\n"
            f"<a href='https://sepolia.basescan.org/address/{CONTRACT_ADDRESS}'>View Contract</a>"
        )

        success = await send_telegram_message(message)
        return {
            "status": "success" if success else "failed",
            "message_sent": success,
        }

    except Exception as e:
        logger.error(f"Error processing score update event: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhook/score-queried")
async def on_score_queried(event: dict):
    """Webhook for ScoreQueried events from AgentFICO contract.
    
    Expected format:
    {
        "agent": "0x...",
        "overall": 336,
        "queriedBy": "0x...",
        "timestamp": "2026-01-29T15:00:00Z"
    }
    """
    try:
        agent = event.get("agent", "unknown")
        overall = event.get("overall", 0)
        queried_by = event.get("queriedBy", "unknown")
        timestamp = event.get("timestamp", datetime.utcnow().isoformat())

        message = (
            f"<b>🔍 Agent Score Queried</b>\n\n"
            f"<b>Agent:</b> <code>{agent[:10]}...{agent[-4:]}</code>\n"
            f"<b>Score:</b> <code>{overall}</code>\n"
            f"<b>Queried By:</b> <code>{queried_by[:10]}...{queried_by[-4:]}</code>\n"
            f"<b>Time:</b> {timestamp}\n\n"
            f"<a href='https://sepolia.basescan.org/address/{CONTRACT_ADDRESS}'>View Contract</a>"
        )

        success = await send_telegram_message(message)
        return {
            "status": "success" if success else "failed",
            "message_sent": success,
        }

    except Exception as e:
        logger.error(f"Error processing score queried event: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhook/generic")
async def on_generic_event(event: dict):
    """Generic webhook for any contract event.
    
    Expected format:
    {
        "event_type": "ScoreUpdated",
        "data": {...}
    }
    """
    try:
        event_type = event.get("event_type", "Unknown")
        data = event.get("data", {})

        message = (
            f"<b>📍 Contract Event: {event_type}</b>\n\n"
            f"<pre>{json.dumps(data, indent=2)}</pre>"
        )

        success = await send_telegram_message(message)
        return {
            "status": "success" if success else "failed",
            "event_type": event_type,
            "message_sent": success,
        }

    except Exception as e:
        logger.error(f"Error processing generic event: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AgentFICO Webhook Listener",
        "version": "0.1.0",
        "endpoints": {
            "/health": "Health check",
            "/webhook/score-updated": "ScoreUpdated events",
            "/webhook/score-queried": "ScoreQueried events",
            "/webhook/generic": "Generic events",
        },
    }
