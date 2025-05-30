"""
Enhanced Sonarr exporter with intelligent features and performance optimizations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from .enhanced_base import EnhancedBaseExporter, ExportConfig
from ..models import MediaFile


class EnhancedSonarrExporter(EnhancedBaseExporter):
    """Next-generation Sonarr exporter with advanced analytics."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.series_cache: Dict[int, Dict] = {}
    
    def get_service_type(self) -> str:
        return "sonarr"
    
    def collect_items(self) -> List[Tuple[Dict, int]]:
        """Collect episodes and their file IDs with rich metadata."""
        self.logger.info("Collecting series and episodes from Sonarr...")
        
        if self.progress:
            self.progress.current_phase = "Collecting series"
        
        # First, get all series
        series_data = self.client.make_request("/api/v3/series")
        if not series_data:
            self.logger.warning("No series found or API request failed")
            return []
        
        # Cache series information
        for series in series_data:
            if 'id' in series:
                self.series_cache[series['id']] = {
                    'title': series.get('title', 'Unknown'),
                    'quality_profile_id': series.get('qualityProfileId'),
                    'tvdb_id': series.get('tvdbId'),
                    'network': series.get('network'),
                    'genres': series.get('genres', []),
                    'year': series.get('year'),
                    'status': series.get('status'),
                    'monitored': series.get('monitored', False)
                }
        
        self.logger.info(f"Found {len(self.series_cache)} series")
        
        if self.progress:
            self.progress.current_phase = "Collecting episodes"
        
        items = []
        processed_series = 0
        
        # Get episodes for each series
        for series_id, series_info in self.series_cache.items():
            processed_series += 1
            
            if processed_series % 20 == 0:
                self.logger.info(f"Processing series {processed_series}/{len(self.series_cache)}")
            
            episodes = self.client.make_request("/api/v3/episode", {"seriesId": series_id})
            if not episodes:
                continue
            
            for episode in episodes:
                if not episode.get("hasFile") or not episode.get("episodeFileId"):
                    continue
                
                file_id = episode["episodeFileId"]
                
                # Extract rich episode metadata
                item_info = {
                    # Basic info
                    "series_id": series_id,
                    "series_title": series_info["title"],
                    "season_number": episode.get("seasonNumber", 0),
                    "episode_number": episode.get("episodeNumber", 0),
                    "episode_title": episode.get("title", "N/A"),
                    "quality_profile_id": series_info["quality_profile_id"],
                    
                    # Series metadata
                    "tvdb_id": series_info.get("tvdb_id"),
                    "network": series_info.get("network"),
                    "series_year": series_info.get("year"),
                    "series_status": series_info.get("status"),
                    "series_monitored": series_info.get("monitored"),
                    "series_genres": series_info.get("genres", []),
                    
                    # Episode metadata
                    "air_date": episode.get("airDate"),
                    "runtime": episode.get("runtime"),
                    "overview": episode.get("overview"),
                    "monitored": episode.get("monitored", False),
                    "episode_id": episode.get("id"),
                    
                    # Dates
                    "downloaded_date": episode.get("grabDate")
                }
                
                items.append((item_info, file_id))
        
        self.logger.info(f"Collected {len(items)} episodes with files")
        return items
    
    def fetch_file_details(self, file_id: int) -> Optional[Dict]:
        """Fetch detailed episode file information."""
        return self.client.make_request(f"/api/v3/episodeFile/{file_id}")
    
    def create_media_file(self, item_info: Dict, file_details: Dict) -> MediaFile:
        """Create enhanced MediaFile object for Sonarr."""
        # Calculate scores and extract formats
        total_score = self.calculate_total_score(file_details)
        custom_formats = self.extract_custom_formats(file_details)
        
        # Extract technical details from mediaInfo
        media_info = file_details.get("mediaInfo", {})
        
        # Get quality profile name
        profile_id = item_info.get("quality_profile_id")
        profile_name = self.quality_profiles.get(profile_id, f"Unknown ID: {profile_id}")
        
        # Format episode display name
        series_title = item_info.get("series_title", "Unknown Series")
        season_num = item_info.get("season_number", 0)
        episode_num = item_info.get("episode_number", 0)
        episode_title = item_info.get("episode_title", "")
        
        if episode_title and episode_title != "N/A":
            display_title = f"{series_title} - S{season_num:02d}E{episode_num:02d} - {episode_title}"
        else:
            display_title = f"{series_title} - S{season_num:02d}E{episode_num:02d}"
        
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
            relative_path=file_details.get("relativePath", "N/A"),
            title=display_title,
            
            # Scores and formats
            total_score=total_score,
            custom_formats=custom_formats,
            
            # Quality information
            quality_profile_id=profile_id or 0,
            quality_profile_name=profile_name,
            quality=self._extract_quality_string(file_details),
            codec=self._extract_codec(media_info),
            resolution=self._extract_resolution(media_info),
            size_bytes=file_details.get("size"),
            
            # Timestamps
            recorded_at=datetime.now(),
            file_modified_at=file_modified_at,
            
            # Service type
            service_type="sonarr",
            
            # TV-specific metadata
            series_id=item_info.get("series_id"),
            season_number=season_num,
            episode_number=episode_num,
            episode_title=episode_title if episode_title != "N/A" else None,
            tvdb_id=item_info.get("tvdb_id")
        )
    
    def _extract_quality_string(self, file_details: Dict) -> Optional[str]:
        """Extract quality string from file details."""
        quality_obj = file_details.get("quality", {})
        if quality_obj and isinstance(quality_obj, dict):
            quality_name = quality_obj.get("quality", {}).get("name")
            if quality_name:
                return quality_name
        return None
    
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
        """Get CSV column names for Sonarr export."""
        return [
            "Series_Title",
            "Episode",
            "Episode_Title",
            "File",
            "Total_Score",
            "Quality_Profile",
            "Quality",
            "Resolution",
            "Codec",
            "Size_GB",
            "Network",
            "Air_Date",
            "TVDB_ID",
            "Custom_Formats",
            "Recorded_At"
        ]
    
    def _media_file_to_csv_row(self, media_file: MediaFile) -> Dict[str, Any]:
        """Convert MediaFile to CSV row for Sonarr."""
        # Calculate size in GB
        size_gb = None
        if media_file.size_bytes:
            size_gb = round(media_file.size_bytes / (1024**3), 2)
        
        # Format custom formats list
        custom_formats_str = "; ".join([
            f"{cf.name} ({cf.score:+d})" for cf in media_file.custom_formats
        ]) if media_file.custom_formats else ""
        
        # Get series info from cache
        series_info = self.series_cache.get(media_file.series_id, {})
        
        # Format episode identifier
        episode_id = f"S{media_file.season_number:02d}E{media_file.episode_number:02d}"
        
        return {
            "Series_Title": series_info.get("title", "Unknown"),
            "Episode": episode_id,
            "Episode_Title": media_file.episode_title or "",
            "File": media_file.relative_path,
            "Total_Score": media_file.total_score,
            "Quality_Profile": media_file.quality_profile_name,
            "Quality": media_file.quality or "",
            "Resolution": media_file.resolution or "",
            "Codec": media_file.codec or "",
            "Size_GB": size_gb or "",
            "Network": series_info.get("network", ""),
            "Air_Date": "",  # Would need to add air_date to MediaFile
            "TVDB_ID": media_file.tvdb_id or "",
            "Custom_Formats": custom_formats_str,
            "Recorded_At": media_file.recorded_at.strftime("%Y-%m-%d %H:%M:%S")
        }