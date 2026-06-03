import os
import base64
import requests
import json
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class AIClient:
    """Helper client to invoke Google Gemini 2.5 Flash API via HTTP requests."""

    @staticmethod
    def get_api_key() -> str:
        return Config.GEMINI_API_KEY

    @staticmethod
    def call_gemini(prompt: str, image_bytes: bytes = None, image_mime_type: str = "image/png") -> str:
        api_key = AIClient.get_api_key()
        if not api_key:
            logger.error("GEMINI_API_KEY is not configured in the environment.")
            return "Error: GEMINI_API_KEY is not configured."

        # Use Gemini 2.5 Flash model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        parts = [{"text": prompt}]

        if image_bytes:
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            parts.append({
                "inlineData": {
                    "mimeType": image_mime_type,
                    "data": image_b64
                }
            })

        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ]
        }

        try:
            logger.info("Sending request to Google Gemini API...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                try:
                    text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    logger.info("Gemini API call completed successfully.")
                    return text_response
                except (KeyError, IndexError) as e:
                    logger.error(f"Failed to parse Gemini response structure: {e}. Raw response: {data}")
                    return f"Error: Failed to parse Gemini response. Raw: {data}"
            else:
                logger.error(f"Gemini API returned error status {response.status_code}: {response.text}")
                return f"Error: Gemini API status {response.status_code}. Response: {response.text}"
        except Exception as e:
            logger.error(f"Exception raised during Gemini API call: {str(e)}")
            return f"Error: Exception during Gemini API call: {str(e)}"
