"""Base exporter class for Radarr/Sonarr score exports."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..api_client import ArrApiClient, ExternalApiClient
from ..config import Config

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Base class for Arr score exporters implementing template method pattern."""
    
    def __init__(self, config: Config, service_name: str):
        """Initialize base exporter."""
        self.config = config
        self.service_name = service_name
        self.external_client = ExternalApiClient()
        self._quality_profiles_cache: Optional[Dict[int, str]] = None
        
        # Initialize service-specific API client
        self.api_client = self._create_api_client()
    
    @abstractmethod
    def _create_api_client(self) -> ArrApiClient:
        """Create service-specific API client."""
        pass
    
    @abstractmethod
    def _get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items (movies/series) from the service."""
        pass
    
    @abstractmethod
    def _extract_external_ids(self, item: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extract external IDs (IMDb, TMDb, TVDB) from item."""
        pass
    
    @abstractmethod
    def _update_custom_formats(self, item_id: int, scores: Dict[str, float]) -> bool:
        """Update custom formats with scores."""
        pass
    
    def export_scores(self, max_workers: int = 5) -> Dict[str, int]:
        """Export scores using template method pattern."""
        logger.info(f"Starting {self.service_name} score export...")
        
        # Step 1: Get all items
        items = self._get_all_items()
        if not items:
            logger.warning(f"No items found in {self.service_name}")
            return {"processed": 0, "updated": 0, "errors": 0}
        
        logger.info(f"Found {len(items)} items in {self.service_name}")
        
        # Step 2: Process items in parallel
        results = {"processed": 0, "updated": 0, "errors": 0}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(self._process_item, item): item 
                for item in items
            }
            
            # Process completed tasks
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    was_updated = future.result()
                    results["processed"] += 1
                    if was_updated:
                        results["updated"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing {item.get('title', 'Unknown')}: {e}")
                    results["errors"] += 1
        
        logger.info(f"{self.service_name} export complete: {results}")
        return results
    
    def _process_item(self, item: Dict[str, Any]) -> bool:
        """Process a single item (movie/series)."""
        try:
            # Extract external IDs
            external_ids = self._extract_external_ids(item)
            
            if not any(external_ids.values()):
                logger.debug(f"No external IDs for: {item.get('title')}")
                return False
            
            # Get scores from external APIs
            scores = self._get_scores(external_ids)
            
            if not scores:
                logger.debug(f"No scores found for: {item.get('title')}")
                return False
            
            # Update custom formats
            return self._update_custom_formats(item['id'], scores)
            
        except Exception as e:
            logger.error(f"Error processing item {item.get('title', 'Unknown')}: {e}")
            return False
    
    def _get_scores(self, external_ids: Dict[str, Optional[str]]) -> Dict[str, float]:
        """Get scores from external APIs."""
        # For now, return empty scores as external API scoring is not implemented
        return {}
    
    def _get_quality_profiles(self) -> Dict[int, str]:
        """Get and cache quality profiles."""
        if self._quality_profiles_cache is None:
            try:
                response = self.api_client.get("api/v3/qualityprofile")
                if response:
                    profiles = response.json()
                    self._quality_profiles_cache = {
                        profile['id']: profile['name'] 
                        for profile in profiles
                    }
                else:
                    self._quality_profiles_cache = {}
            except Exception as e:
                logger.error(f"Error fetching quality profiles: {e}")
                self._quality_profiles_cache = {}
        
        return self._quality_profiles_cache
    
    def test_connection(self) -> bool:
        """Test connection to the service."""
        return self.api_client.test_connection()
