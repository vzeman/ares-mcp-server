"""ARES API client implementation with error handling and rate limiting."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        async with self._lock:
            now = datetime.now()
            # Remove old requests outside the time window
            self.requests = [
                req_time for req_time in self.requests
                if now - req_time < timedelta(seconds=self.time_window)
            ]
            
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = self.requests[0]
                wait_time = (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)
                    # Recursive call to recheck after waiting
                    await self.acquire()
            else:
                self.requests.append(now)


class AresSubject(BaseModel):
    """ARES subject data model."""
    ico: str = Field(..., description="Company identification number (IČO)")
    name: str = Field(..., description="Company name")
    legal_form: Optional[str] = Field(None, description="Legal form of the company")
    address: Optional[Dict[str, Any]] = Field(None, description="Company address")
    registration_date: Optional[str] = Field(None, description="Registration date")
    status: Optional[str] = Field(None, description="Company status")


class AresAPIClient:
    """Client for interacting with ARES API."""
    
    BASE_URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest"
    
    def __init__(self, rate_limit_requests: int = 100, rate_limit_window: int = 60):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/json",
                "User-Agent": "ARES-MCP-Server/0.1.0"
            },
            timeout=30.0
        )
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make rate-limited HTTP request to ARES API."""
        await self.rate_limiter.acquire()
        
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"text": response.text}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            error_detail = f"HTTP {e.response.status_code}"
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_detail += f": {error_json['detail']}"
            except:
                pass
            raise Exception(f"ARES API error: {error_detail}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
    
    async def search_subject(self, ico: Optional[str] = None, 
                           name: Optional[str] = None,
                           address: Optional[str] = None) -> str:
        """Search for economic subjects in ARES."""
        params = {}
        if ico:
            params["ico"] = ico
        if name:
            params["obchodniJmeno"] = name
        if address:
            params["sidlo"] = address
        
        if not params:
            return json.dumps({
                "error": "At least one search parameter (ico, name, or address) is required"
            }, indent=2)
        
        try:
            result = await self._make_request(
                "GET", 
                "/ekonomicke-subjekty-vyhledat",
                params=params
            )
            
            # Format the response
            if isinstance(result, dict) and "ekonomickeSubjekty" in result:
                subjects = result["ekonomickeSubjekty"]
                formatted_subjects = []
                
                for subject in subjects:
                    formatted_subject = {
                        "ico": subject.get("ico"),
                        "name": subject.get("obchodniJmeno"),
                        "address": self._format_address(subject.get("sidlo", {})),
                        "legal_form": subject.get("pravniForma"),
                        "status": subject.get("stavSubjektu")
                    }
                    formatted_subjects.append(formatted_subject)
                
                return json.dumps({
                    "found": len(formatted_subjects),
                    "subjects": formatted_subjects
                }, indent=2, ensure_ascii=False)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def get_subject(self, ico: str) -> str:
        """Get detailed information about a specific subject."""
        try:
            result = await self._make_request(
                "GET",
                f"/ekonomicke-subjekty/{ico}"
            )
            
            # Format the detailed response
            if isinstance(result, dict):
                formatted_result = {
                    "ico": result.get("ico"),
                    "dic": result.get("dic"),
                    "name": result.get("obchodniJmeno"),
                    "legal_form": result.get("pravniForma"),
                    "establishment_date": result.get("datumVzniku"),
                    "termination_date": result.get("datumZaniku"),
                    "status": result.get("stavSubjektu"),
                    "address": self._format_address(result.get("sidlo", {})),
                    "statutory_body": result.get("statutarniOrgan"),
                    "activities": result.get("cinnosti", [])
                }
                return json.dumps(formatted_result, indent=2, ensure_ascii=False)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def get_extract(self, ico: str, extract_type: str = "standard") -> str:
        """Get business register extract for a subject."""
        try:
            endpoint = f"/ekonomicke-subjekty/{ico}/vypis-{extract_type}"
            result = await self._make_request("GET", endpoint)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def validate_ico(self, ico: str) -> str:
        """Validate if ICO exists and is valid."""
        try:
            # ICO validation algorithm
            if not ico or not ico.isdigit() or len(ico) != 8:
                return json.dumps({
                    "valid": False,
                    "reason": "ICO must be exactly 8 digits"
                }, indent=2)
            
            # Check modulo 11 algorithm
            weights = [8, 7, 6, 5, 4, 3, 2]
            total = sum(int(ico[i]) * weights[i] for i in range(7))
            check_digit = (11 - (total % 11)) % 10
            
            is_valid_format = check_digit == int(ico[7])
            
            # Check if exists in ARES
            exists = False
            if is_valid_format:
                try:
                    await self._make_request("GET", f"/ekonomicke-subjekty/{ico}")
                    exists = True
                except:
                    exists = False
            
            return json.dumps({
                "ico": ico,
                "valid_format": is_valid_format,
                "exists_in_ares": exists,
                "valid": is_valid_format and exists
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def _format_address(self, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format address data for better readability."""
        if not address_data:
            return {}
        
        return {
            "street": address_data.get("nazevUlice"),
            "building_number": address_data.get("cisloDomovni"),
            "orientation_number": address_data.get("cisloOrientacni"),
            "city": address_data.get("nazevObce"),
            "city_part": address_data.get("nazevCastiObce"),
            "postal_code": address_data.get("psc"),
            "country": address_data.get("nazevStatu", "Česká republika")
        }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()