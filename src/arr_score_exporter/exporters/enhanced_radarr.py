"""
Enhanced Radarr exporter with intelligent features and performance optimizations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from .enhanced_base import EnhancedBaseExporter, ExportConfig
from ..models import MediaFile


class EnhancedRadarrExporter(EnhancedBaseExporter):
    """Next-generation Radarr exporter with advanced analytics."""
    
    def get_service_type(self) -> str:
        return "radarr"
    
    def collect_items(self) -> List[Tuple[Dict, int]]:
        """Collect movies and their file IDs with rich metadata."""
        self.logger.info("Collecting movies from Radarr...")
        
        if self.progress:
            self.progress.current_phase = "Collecting movies"
        
        movies = self.client.make_request("/api/v3/movie")
        if not movies:
            self.logger.warning("No movies found or API request failed")
            return []
        
        self.logger.info(f"Found {len(movies)} movies")
        
        items = []
        for movie in movies:
            if not movie.get("hasFile"):
                continue
                
            movie_file = movie.get("movieFile", {})
            file_id = movie_file.get("id")
            
            if not file_id:
                continue
            
            # Extract rich metadata
            item_info = {
                # Basic info
                "title": movie.get("title", "N/A"),
                "year": movie.get("year"),
                "file_path": movie_file.get("relativePath", "N/A"),
                "quality_profile_id": movie.get("qualityProfileId"),
                
                # Movie-specific metadata
                "movie_id": movie.get("id"),
                "imdb_id": movie.get("imdbId"),
                "tmdb_id": movie.get("tmdbId"),
                "runtime": movie.get("runtime"),
                "genres": movie.get("genres", []),
                "certification": movie.get("certification"),
                "studio": movie.get("studio"),
                
                # Quality info from movie file summary
                "size_bytes": movie_file.get("size"),
                "quality": movie_file.get("quality", {}).get("quality", {}).get("name"),
                "mediaInfo": movie_file.get("mediaInfo", {}),
                
                # Dates
                "added_date": movie.get("added"),
                "monitored": movie.get("monitored", False),
                "downloaded_date": movie_file.get("dateAdded")
            }
            
            items.append((item_info, file_id))
        
        self.logger.info(f"Collected {len(items)} movies with files")
        return items
    
    def fetch_file_details(self, file_id: int) -> Optional[Dict]:
        """Fetch detailed movie file information."""
        return self.client.make_request(f"/api/v3/movieFile/{file_id}")
    
    def create_media_file(self, item_info: Dict, file_details: Dict) -> MediaFile:
        """Create enhanced MediaFile object for Radarr."""
        # Calculate scores and extract formats
        total_score = self.calculate_total_score(file_details)
        custom_formats = self.extract_custom_formats(file_details)
        
        # Extract technical details from mediaInfo
        media_info = file_details.get("mediaInfo", {}) or item_info.get("mediaInfo", {})
        
        # Get quality profile name
        profile_id = item_info.get("quality_profile_id")
        profile_name = self.quality_profiles.get(profile_id, f"Unknown ID: {profile_id}")
        
        # Parse file modification time
        file_modified_at = None
        if file_details.get("dateAdded"):
            try:
                file_modified_at = datetime.fromisoformat(
                    file_details["dateAdded"].replace('Z', '+00:00')
                )
            except (ValueError, TypeError):
                pass
        
        return MediaFile(
            # Core identification
            file_id=file_details.get("id", 0),
            relative_path=file_details.get("relativePath", item_info.get("file_path", "N/A")),
            title=item_info.get("title", "N/A"),
            
            # Scores and formats
            total_score=total_score,
            custom_formats=custom_formats,
            
            # Quality information
            quality_profile_id=profile_id or 0,
            quality_profile_name=profile_name,
            quality=self._extract_quality_string(file_details, item_info),
            codec=self._extract_codec(media_info),
            resolution=self._extract_resolution(media_info),
            size_bytes=file_details.get("size") or item_info.get("size_bytes"),
            
            # Timestamps
            recorded_at=datetime.now(),
            file_modified_at=file_modified_at,
            
            # Service type
            service_type="radarr",
            
            # Movie-specific metadata
            movie_id=item_info.get("movie_id"),
            imdb_id=item_info.get("imdb_id"),
            tmdb_id=item_info.get("tmdb_id")
        )
    
    def _extract_quality_string(self, file_details: Dict, item_info: Dict) -> Optional[str]:
        """Extract quality string from file details."""
        # Try from file details first
        quality_obj = file_details.get("quality", {})
        if quality_obj and isinstance(quality_obj, dict):
            quality_name = quality_obj.get("quality", {}).get("name")
            if quality_name:
                return quality_name
        
        # Fallback to item info
        return item_info.get("quality")
    
    def _extract_codec(self, media_info: Dict) -> Optional[str]:
        """Extract codec information from mediaInfo."""
        if not media_info:
            return None
        
        # Try video codec first
        video_codec = media_info.get("videoCodec")
        if video_codec:
            return video_codec
        
        # Try audio codec as fallback
        audio_codec = media_info.get("audioCodec")
        if audio_codec:
            return f"Audio: {audio_codec}"
        
        return None
    
    def _extract_resolution(self, media_info: Dict) -> Optional[str]:
        """Extract resolution from mediaInfo."""
        if not media_info:
            return None
        
        # Try direct resolution field
        resolution = media_info.get("resolution")
        if resolution:
            return resolution
        
        # Try to construct from width/height
        width = media_info.get("width")
        height = media_info.get("height")
        
        if width and height:
            # Map common resolutions
            if height >= 2160:
                return "2160p"
            elif height >= 1440:
                return "1440p"
            elif height >= 1080:
                return "1080p"
            elif height >= 720:
                return "720p"
            elif height >= 480:
                return "480p"
            else:
                return f"{width}x{height}"
        
        return None
    
    def _get_csv_fieldnames(self) -> List[str]:
        """Get CSV column names for Radarr export."""
        return [
            "Title",
            "Year", 
            "File",
            "Total_Score",
            "Quality_Profile",
            "Quality",
            "Resolution",
            "Codec",
            "Size_GB",
            "IMDB_ID",
            "TMDB_ID",
            "Custom_Formats",
            "Recorded_At"
        ]
    
    def _media_file_to_csv_row(self, media_file: MediaFile) -> Dict[str, Any]:
        """Convert MediaFile to CSV row for Radarr."""
        # Calculate size in GB
        size_gb = None
        if media_file.size_bytes:
            size_gb = round(media_file.size_bytes / (1024**3), 2)
        
        # Format custom formats list
        custom_formats_str = "; ".join([
            f"{cf.name} ({cf.score:+d})" for cf in media_file.custom_formats
        ]) if media_file.custom_formats else ""
        
        return {
            "Title": media_file.title,
            "Year": getattr(media_file, 'year', ''),  # Would need to add year to MediaFile
            "File": media_file.relative_path,
            "Total_Score": media_file.total_score,
            "Quality_Profile": media_file.quality_profile_name,
            "Quality": media_file.quality or "",
            "Resolution": media_file.resolution or "",
            "Codec": media_file.codec or "",
            "Size_GB": size_gb or "",
            "IMDB_ID": media_file.imdb_id or "",
            "TMDB_ID": media_file.tmdb_id or "",
            "Custom_Formats": custom_formats_str,
            "Recorded_At": media_file.recorded_at.strftime("%Y-%m-%d %H:%M:%S")
        }