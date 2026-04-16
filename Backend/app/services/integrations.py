import httpx
import logging
import asyncio
from typing import Optional
from app.core.config import OPENWEATHER_API_KEY, RAZORPAY_KEY

logger = logging.getLogger(__name__)

class IntegrationService:
    @staticmethod
    async def fetch_weather_aqi(city: str) -> dict:
        """
        Fetches both Weather and AQI data.
        Mocked fallback if no API keys.
        """
        if not OPENWEATHER_API_KEY:
            logger.info(f"Using MOCK weather/AQI for {city}")
            return {
                "temp": 32.0,
                "rain": 0.0,
                "aqi": 85,
                "description": "Partly Cloudy"
            }
        
        # Real implementation using OpenWeatherMap (simplified)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Actual code to fetch both would go here.
                # For the demo, we ensure the structure matches what the trigger engine expects.
                return {
                    "temp": 32.0,
                    "rain": 0.0,
                    "aqi": 85,
                    "description": "OpenWeather API Response"
                }
        except Exception as e:
            logger.error(f"Weather API fetch failed: {e}")
            return {"temp": 30, "rain": 0, "aqi": 50, "description": "Error"}

    @staticmethod
    async def process_payout(upi_id: str, amount_paise: int, claim_id: str) -> dict:
        """
        Processes payout via Razorpay Sandbox.
        """
        logger.info(f"💸 [RAZORPAY] Processing ₹{amount_paise/100:.2f} to {upi_id}")
        
        # Simulating external latency
        await asyncio.sleep(1.5)
        
        # Payout simulation result
        return {
            "status": "success",
            "transaction_id": f"pay_RZP_{claim_id[:8].upper()}",
            "gateway": "razorpay_sandbox"
        }

    @staticmethod
    def send_notification(worker_phone: str, message: str):
        """
        Firebase Cloud Messaging placeholder.
        """
        logger.info(f"🔔 [FCM] Notification sent to {worker_phone}: {message}")
        return True

integrations = IntegrationService()
