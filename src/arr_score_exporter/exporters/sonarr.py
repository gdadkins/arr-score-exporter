"""Sonarr-specific score exporter."""

import logging
from typing import Dict, List, Optional, Any

from .base import BaseExporter
from ..api_client import ArrApiClient
from ..config import Config

logger = logging.getLogger(__name__)


class SonarrExporter(BaseExporter):
    """Sonarr-specific score exporter."""
    
    def __init__(self, config: Config):
        """Initialize Sonarr exporter."""
        super().__init__(config, "Sonarr")
    
    def _create_api_client(self) -> ArrApiClient:
        """Create Sonarr API client."""
        return ArrApiClient(
            base_url=self.config.sonarr_url,
            api_key=self.config.sonarr_api_key,
            name="Sonarr"
        )
    
    def _get_all_items(self) -> List[Dict[str, Any]]:
        """Get all series from Sonarr."""
        try:
            response = self.api_client.get("api/v3/series")
            if response:
                series = response.json()
                logger.info(f"Retrieved {len(series)} series from Sonarr")
                return series
            else:
                logger.error("Failed to retrieve series from Sonarr")
                return []
        except Exception as e:
            logger.error(f"Error fetching series from Sonarr: {e}")
            return []
    
    def _extract_external_ids(self, item: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extract external IDs from Sonarr series."""
        return {
            'imdb_id': item.get('imdbId'),
            'tmdb_id': None,  # Will be resolved from TVDB
            'tvdb_id': str(item.get('tvdbId')) if item.get('tvdbId') else None
        }
    
    
    def _update_custom_formats(self, item_id: int, scores: Dict[str, float]) -> bool:
        """Update custom formats in Sonarr with scores."""
        try:
            # Get current series details
            response = self.api_client.get(f"api/v3/series/{item_id}")
            if not response:
                logger.error(f"Failed to get series details for ID {item_id}")
                return False
            
            series = response.json()
            
            # Check if series has custom formats
            if 'customFormats' not in series:
                series['customFormats'] = []
            
            # Update custom formats with scores
            updated = False
            for score_type, score_value in scores.items():
                format_name = self._get_custom_format_name(score_type)
                
                # Find existing custom format or create new one
                custom_format = self._find_or_create_custom_format(format_name, score_value)
                if custom_format:
                    # Add to series's custom formats if not already present
                    format_exists = any(
                        cf.get('id') == custom_format['id'] 
                        for cf in series.get('customFormats', [])
                    )
                    
                    if not format_exists:
                        series['customFormats'].append(custom_format)
                        updated = True
            
            # Update series if changes were made
            if updated:
                update_response = self.api_client.put(f"api/v3/series/{item_id}", json=series)
                if update_response:
                    logger.debug(f"Updated custom formats for series ID {item_id}")
                    return True
                else:
                    logger.error(f"Failed to update series ID {item_id}")
                    return False
            
            return False  # No updates needed
            
        except Exception as e:
            logger.error(f"Error updating custom formats for series ID {item_id}: {e}")
            return False
    
    def _get_custom_format_name(self, score_type: str) -> str:
        """Get custom format name for score type."""
        format_mapping = {
            'tmdb': self.config.get('export.custom_formats.tmdb_score', 'TMDb Score'),
            'imdb': self.config.get('export.custom_formats.imdb_score', 'IMDb Score')
        }
        return format_mapping.get(score_type, f"{score_type.upper()} Score")
    
    def _find_or_create_custom_format(self, name: str, score: float) -> Optional[Dict[str, Any]]:
        """Find existing custom format or create placeholder for new one."""
        try:
            # Get all custom formats
            response = self.api_client.get("api/v3/customformat")
            if response:
                custom_formats = response.json()
                
                # Look for existing format with this name
                for cf in custom_formats:
                    if cf.get('name') == name:
                        return cf
                
                # For now, we'll just log that we would create a new format
                # In a full implementation, you would create the custom format here
                logger.info(f"Would create custom format '{name}' with score {score}")
                return None
            
        except Exception as e:
            logger.error(f"Error finding/creating custom format '{name}': {e}")
        
        return None
