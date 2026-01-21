from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
from dotenv import load_dotenv
import logging
import json
import hmac
import hashlib
import base64
import time
import urllib.parse
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Prometheus Alertmanager Webhook Service", description="A webhook service that receives Prometheus Alertmanager alerts and forwards them to DingTalk robots")

# Configuration
DINGTALK_WEBHOOK_URL = os.getenv("DINGTALK_WEBHOOK_URL")
DINGTALK_SECRET = os.getenv("DINGTALK_SECRET")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Setup Jinja2 template environment
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(template_dir),
    trim_blocks=True,
    lstrip_blocks=True
)

def generate_dingtalk_signature(secret: str) -> tuple[str, str]:
    """
    Generate DingTalk robot signature for signed security mode

    Args:
        secret: The DingTalk robot secret

    Returns:
        tuple: (timestamp, signature)
    """
    timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds
    string_to_sign = f"{timestamp}\n{secret}"

    # Calculate HMAC-SHA256 signature
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()

    # Base64 encode and URL encode the signature
    signature = urllib.parse.quote(base64.b64encode(hmac_code).decode('utf-8'))

    return timestamp, signature

def select_template(alerts: list) -> str:
    """
    Select appropriate template based on alert content

    Args:
        alerts: List of alert objects

    Returns:
        str: Template filename
    """
    if not alerts:
        return "alert_template.j2"

    # Check the first alert's labels and annotations for keywords
    first_alert = alerts[0]
    alertname = first_alert.get("labels", {}).get("alertname", "").lower()
    summary = first_alert.get("annotations", {}).get("summary", "").lower()
    description = first_alert.get("annotations", {}).get("description", "").lower()

    # Certificate expiry alerts
    cert_keywords = ["tls", "证书", "ssl", "certificate", "过期", "expiry", "expir"]
    if any(keyword in alertname or keyword in summary or keyword in description for keyword in cert_keywords):
        return "certificate_expiry_template.j2"

    # Service down alerts
    down_keywords = ["down", "宕机", "unreachable", "unavailable", "故障", "failed"]
    if any(keyword in alertname or keyword in summary or keyword in description for keyword in down_keywords):
        return "service_down_template.j2"

    # Default template
    return "alert_template.j2"

def send_dingtalk_message(message: str, msg_type: str = "text") -> bool:
    """
    Send message to DingTalk robot

    Args:
        message: The message content to send
        msg_type: Type of message (text, markdown, etc.)

    Returns:
        bool: True if successful, False otherwise
    """
    if not DINGTALK_WEBHOOK_URL:
        logger.error("DINGTALK_WEBHOOK_URL not configured")
        return False

    # Generate signature if secret is configured (signed security mode)
    webhook_url = DINGTALK_WEBHOOK_URL
    if DINGTALK_SECRET:
        timestamp, signature = generate_dingtalk_signature(DINGTALK_SECRET)
        # Add signature parameters to URL
        separator = "&" if "?" in webhook_url else "?"
        webhook_url = f"{webhook_url}{separator}timestamp={timestamp}&sign={signature}"
        logger.debug(f"Using signed webhook URL for DingTalk")

    headers = {"Content-Type": "application/json"}

    if msg_type == "text":
        payload = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
    elif msg_type == "markdown":
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "Prometheus Alert",
                "text": message
            }
        }
    else:
        logger.error(f"Unsupported message type: {msg_type}")
        return False

    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Message sent to DingTalk successfully")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send message to DingTalk: {e}")
        return False

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Webhook service is running", "status": "healthy"}

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    """
    Main webhook endpoint that receives Prometheus Alertmanager alerts and forwards to DingTalk
    """
    try:
        # Get request data
        data = await request.json()
        logger.info(f"Received Alertmanager webhook: {json.dumps(data, indent=2)}")

        # Extract alert information
        alerts = data.get("alerts", [])
        status = data.get("status", "unknown")
        group_labels = data.get("groupLabels", {})
        external_url = data.get("externalURL", "")

        # Prepare template context
        template_context = {
            "status": status,
            "alerts": alerts,
            "group_labels": group_labels,
            "external_url": external_url
        }

        # Select appropriate template and render message
        try:
            template_name = select_template(alerts)
            logger.info(f"Using template: {template_name}")
            template = jinja_env.get_template(template_name)
            message = template.render(**template_context)
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            # Fallback to basic message if template fails
            message = f"**Prometheus Alert**\n\nStatus: {status}\nAlert Count: {len(alerts)}"

        # Send to DingTalk
        success = send_dingtalk_message(message, msg_type="markdown")

        if success:
            return JSONResponse(content={"status": "success", "message": "Alert notification sent to DingTalk"}, status_code=200)
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification to DingTalk")

    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
