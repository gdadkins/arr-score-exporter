"""CSV utilities for exporting data."""

import csv
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVWriter:
    """Utility class for writing CSV files."""
    
    def __init__(self, output_dir: str = "exports"):
        """Initialize CSV writer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def write_movies_csv(self, movies: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Write movies data to CSV file."""
        if filename is None:
            filename = "radarr_movies_export.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if not movies:
                    logger.warning("No movies data to write")
                    return str(filepath)
                
                # Define fieldnames based on first movie
                fieldnames = [
                    'id', 'title', 'year', 'imdbId', 'tmdbId', 'status',
                    'monitored', 'qualityProfileId', 'path', 'added',
                    'tmdb_score', 'imdb_score', 'custom_formats'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for movie in movies:
                    row = self._format_movie_row(movie)
                    writer.writerow(row)
                
                logger.info(f"Exported {len(movies)} movies to {filepath}")
                return str(filepath)
                
        except Exception as e:
            logger.error(f"Error writing movies CSV: {e}")
            raise
    
    def write_series_csv(self, series: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Write series data to CSV file."""
        if filename is None:
            filename = "sonarr_series_export.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if not series:
                    logger.warning("No series data to write")
                    return str(filepath)
                
                # Define fieldnames for series
                fieldnames = [
                    'id', 'title', 'year', 'imdbId', 'tvdbId', 'status',
                    'monitored', 'qualityProfileId', 'path', 'added',
                    'tmdb_score', 'imdb_score', 'custom_formats'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for show in series:
                    row = self._format_series_row(show)
                    writer.writerow(row)
                
                logger.info(f"Exported {len(series)} series to {filepath}")
                return str(filepath)
                
        except Exception as e:
            logger.error(f"Error writing series CSV: {e}")
            raise
    
    def _format_movie_row(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """Format movie data for CSV row."""
        return {
            'id': movie.get('id', ''),
            'title': movie.get('title', ''),
            'year': movie.get('year', ''),
            'imdbId': movie.get('imdbId', ''),
            'tmdbId': movie.get('tmdbId', ''),
            'status': movie.get('status', ''),
            'monitored': movie.get('monitored', ''),
            'qualityProfileId': movie.get('qualityProfileId', ''),
            'path': movie.get('path', ''),
            'added': movie.get('added', ''),
            'tmdb_score': movie.get('tmdb_score', ''),
            'imdb_score': movie.get('imdb_score', ''),
            'custom_formats': self._format_custom_formats(movie.get('customFormats', []))
        }
    
    def _format_series_row(self, series: Dict[str, Any]) -> Dict[str, Any]:
        """Format series data for CSV row."""
        return {
            'id': series.get('id', ''),
            'title': series.get('title', ''),
            'year': series.get('year', ''),
            'imdbId': series.get('imdbId', ''),
            'tvdbId': series.get('tvdbId', ''),
            'status': series.get('status', ''),
            'monitored': series.get('monitored', ''),
            'qualityProfileId': series.get('qualityProfileId', ''),
            'path': series.get('path', ''),
            'added': series.get('added', ''),
            'tmdb_score': series.get('tmdb_score', ''),
            'imdb_score': series.get('imdb_score', ''),
            'custom_formats': self._format_custom_formats(series.get('customFormats', []))
        }
    
    def _format_custom_formats(self, custom_formats: List[Dict[str, Any]]) -> str:
        """Format custom formats list as string."""
        if not custom_formats:
            return ''
        
        format_names = [cf.get('name', '') for cf in custom_formats if cf.get('name')]
        return '; '.join(format_names)
    
    def write_scores_summary(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Write export results summary to CSV."""
        if filename is None:
            filename = "export_summary.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['service', 'processed', 'updated', 'errors', 'timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                from datetime import datetime
                timestamp = datetime.now().isoformat()
                
                for service, service_results in results.items():
                    if isinstance(service_results, dict):
                        row = {
                            'service': service,
                            'processed': service_results.get('processed', 0),
                            'updated': service_results.get('updated', 0),
                            'errors': service_results.get('errors', 0),
                            'timestamp': timestamp
                        }
                        writer.writerow(row)
                
                logger.info(f"Exported summary to {filepath}")
                return str(filepath)
                
        except Exception as e:
            logger.error(f"Error writing summary CSV: {e}")
            raise
