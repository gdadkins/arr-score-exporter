"""Shared API client for Arr applications and external services."""

import requests
import time
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class ArrApiClient:
    """Shared API client for Radarr/Sonarr with retry logic and rate limiting."""
    
    def __init__(self, base_url: str, api_key: str, name: str = "ArrClient"):
        """Initialize API client."""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': api_key,
            'User-Agent': 'Arr-Score-Exporter/1.0.0'
        })
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make GET request to API endpoint."""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        return self._make_request("GET", url, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make POST request to API endpoint."""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        return self._make_request("POST", url, data=data, json=json)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make PUT request to API endpoint."""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        return self._make_request("PUT", url, data=data, json=json)
    
    def _make_request(self, method: str, url: str, retry_attempts: int = 3, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and exponential backoff."""
        retry_delay = 1
        
        for attempt in range(retry_attempts):
            try:
                logger.debug(f"{self.name}: {method} {url}")
                response = self.session.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    logger.warning(f"{self.name}: Rate limited, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                    
                logger.error(f"{self.name}: HTTP {response.status_code}: {e}")
                if attempt == retry_attempts - 1:
                    raise
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"{self.name}: Request failed (attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"{self.name}: Request failed after {retry_attempts} attempts")
                    return None
        
        return None
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            response = self.get("api/v3/system/status")
            return response is not None and response.status_code == 200
        except Exception as e:
            logger.error(f"{self.name}: Connection test failed: {e}")
            return False


class ExternalApiClient:
    """Client for external APIs (TMDb, IMDb, etc.)."""
    
    def __init__(self):
        """Initialize external API client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Arr-Score-Exporter/1.0.0'
        })
    
    def get_tmdb_score(self, tmdb_id: Union[str, int], media_type: str, api_key: str) -> Optional[float]:
        """Get score from TMDb API."""
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
        params = {"api_key": api_key}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('vote_average')
        except Exception as e:
            logger.error(f"Error fetching TMDb score for {tmdb_id}: {e}")
            return None
    
    def get_tmdb_id_from_tvdb(self, tvdb_id: Union[str, int], api_key: str) -> Optional[int]:
        """Get TMDb ID using TVDB ID."""
        url = f"https://api.themoviedb.org/3/find/{tvdb_id}"
        params = {
            "api_key": api_key,
            "external_source": "tvdb_id"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            tv_results = data.get('tv_results', [])
            if tv_results:
                return tv_results[0].get('id')
        except Exception as e:
            logger.error(f"Error finding TMDb ID for TVDB {tvdb_id}: {e}")
        
        return None
    
    def get_imdb_score(self, imdb_id: str) -> Optional[float]:
        """Get score from IMDb (placeholder for future implementation)."""
        # TODO: Implement IMDb score fetching
        # This could use web scraping or a third-party API
        logger.debug(f"IMDb score fetching not yet implemented for {imdb_id}")
        return None
