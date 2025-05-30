"""Radarr-specific score exporter."""

import logging
from typing import Dict, List, Optional, Any

from .base import BaseExporter
from ..api_client import ArrApiClient
from ..config import Config

logger = logging.getLogger(__name__)


class RadarrExporter(BaseExporter):
    """Radarr-specific score exporter."""
    
    def __init__(self, config: Config):
        """Initialize Radarr exporter."""
        super().__init__(config, "Radarr")
    
    def _create_api_client(self) -> ArrApiClient:
        """Create Radarr API client."""
        return ArrApiClient(
            base_url=self.config.radarr_url,
            api_key=self.config.radarr_api_key,
            name="Radarr"
        )
    
    def _get_all_items(self) -> List[Dict[str, Any]]:
        """Get all movies from Radarr."""
        try:
            response = self.api_client.get("api/v3/movie")
            if response:
                movies = response.json()
                logger.info(f"Retrieved {len(movies)} movies from Radarr")
                return movies
            else:
                logger.error("Failed to retrieve movies from Radarr")
                return []
        except Exception as e:
            logger.error(f"Error fetching movies from Radarr: {e}")
            return []
    
    def _extract_external_ids(self, item: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extract external IDs from Radarr movie."""
        return {
            'imdb_id': item.get('imdbId'),
            'tmdb_id': str(item.get('tmdbId')) if item.get('tmdbId') else None,
            'tvdb_id': None  # Not applicable for movies
        }
    
    def _get_tmdb_score(self, external_ids: Dict[str, Optional[str]]) -> Optional[float]:
        """Get TMDb score for movie."""
        tmdb_id = external_ids.get('tmdb_id')
        if tmdb_id and self.config.tmdb_api_key:
            return self.external_client.get_tmdb_score(
                tmdb_id=tmdb_id,
                media_type='movie',
                api_key=self.config.tmdb_api_key
            )
        return None
    
    def _update_custom_formats(self, item_id: int, scores: Dict[str, float]) -> bool:
        """Update custom formats in Radarr with scores."""
        try:
            # Get current movie details
            response = self.api_client.get(f"api/v3/movie/{item_id}")
            if not response:
                logger.error(f"Failed to get movie details for ID {item_id}")
                return False
            
            movie = response.json()
            
            # Check if movie has custom formats
            if 'customFormats' not in movie:
                movie['customFormats'] = []
            
            # Update custom formats with scores
            updated = False
            for score_type, score_value in scores.items():
                format_name = self._get_custom_format_name(score_type)
                
                # Find existing custom format or create new one
                custom_format = self._find_or_create_custom_format(format_name, score_value)
                if custom_format:
                    # Add to movie's custom formats if not already present
                    format_exists = any(
                        cf.get('id') == custom_format['id'] 
                        for cf in movie.get('customFormats', [])
                    )
                    
                    if not format_exists:
                        movie['customFormats'].append(custom_format)
                        updated = True
            
            # Update movie if changes were made
            if updated:
                update_response = self.api_client.put(f"api/v3/movie/{item_id}", json=movie)
                if update_response:
                    logger.debug(f"Updated custom formats for movie ID {item_id}")
                    return True
                else:
                    logger.error(f"Failed to update movie ID {item_id}")
                    return False
            
            return False  # No updates needed
            
        except Exception as e:
            logger.error(f"Error updating custom formats for movie ID {item_id}: {e}")
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
