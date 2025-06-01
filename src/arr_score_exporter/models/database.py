"""
Enhanced database models for Arr Score Exporter with historical tracking and analysis.

This module provides a robust data persistence layer for tracking score changes over time,
enabling trend analysis, upgrade candidate identification, and library health monitoring.
"""

import sqlite3
import datetime
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class ScoreChangeType(Enum):
    """Types of score changes for trend analysis."""
    IMPROVED = "improved"
    DEGRADED = "degraded"
    NEW_FILE = "new_file"
    REMOVED = "removed"
    UNCHANGED = "unchanged"


@dataclass
class CustomFormatDetail:
    """Detailed custom format information."""
    name: str
    score: int
    format_id: int
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class MediaFile:
    """Enhanced media file representation with rich metadata."""
    # Core identification (required fields first)
    file_id: int
    relative_path: str
    title: str
    total_score: int
    quality_profile_id: int
    quality_profile_name: str
    
    # Optional fields with defaults
    custom_formats: List[CustomFormatDetail] = field(default_factory=list)
    quality: Optional[str] = None
    codec: Optional[str] = None
    resolution: Optional[str] = None
    size_bytes: Optional[int] = None
    recorded_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    file_modified_at: Optional[datetime.datetime] = None
    service_type: str = "unknown"  # radarr/sonarr
    movie_id: Optional[int] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    series_id: Optional[int] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    episode_title: Optional[str] = None
    tvdb_id: Optional[int] = None
    
    @property
    def unique_identifier(self) -> str:
        """Generate a unique identifier for this media file."""
        if self.service_type == "radarr":
            return f"radarr:{self.movie_id}:{self.file_id}"
        elif self.service_type == "sonarr":
            return f"sonarr:{self.series_id}:S{self.season_number:02d}E{self.episode_number:02d}:{self.file_id}"
        return f"{self.service_type}:{self.file_id}"
    
    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        if self.service_type == "sonarr" and self.episode_title:
            return f"{self.title} - S{self.season_number:02d}E{self.episode_number:02d} - {self.episode_title}"
        return self.title
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_id': self.file_id,
            'relative_path': self.relative_path,
            'title': self.title,
            'total_score': self.total_score,
            'custom_formats': [
                {
                    'name': cf.name,
                    'score': cf.score,
                    'format_id': cf.format_id,
                    'category': cf.category,
                    'tags': cf.tags
                }
                for cf in self.custom_formats
            ],
            'quality_profile_id': self.quality_profile_id,
            'quality_profile_name': self.quality_profile_name,
            'quality': self.quality,
            'codec': self.codec,
            'resolution': self.resolution,
            'size_bytes': self.size_bytes,
            'recorded_at': self.recorded_at.isoformat(),
            'file_modified_at': self.file_modified_at.isoformat() if self.file_modified_at else None,
            'service_type': self.service_type,
            'movie_id': self.movie_id,
            'imdb_id': self.imdb_id,
            'tmdb_id': self.tmdb_id,
            'series_id': self.series_id,
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'tvdb_id': self.tvdb_id
        }


@dataclass
class ScoreHistory:
    """Historical score record for trend analysis."""
    unique_identifier: str
    timestamp: datetime.datetime
    total_score: int
    change_type: ScoreChangeType
    previous_score: Optional[int] = None
    custom_formats_json: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class LibraryStats:
    """Library-wide statistics and health metrics."""
    timestamp: datetime.datetime
    service_type: str
    
    # Count metrics
    total_files: int
    files_with_positive_scores: int
    files_with_negative_scores: int
    files_with_zero_scores: int
    
    # Score distribution
    min_score: int
    max_score: int
    avg_score: float
    median_score: float
    
    # Quality profiles
    quality_profiles: Dict[str, int]  # profile_name -> file_count
    
    # Custom format effectiveness
    most_common_formats: List[Tuple[str, int, int]]  # (name, count, avg_score)
    
    # Size and quality metrics
    total_size_gb: float
    avg_file_size_gb: float
    resolution_distribution: Dict[str, int]
    codec_distribution: Dict[str, int]


class DatabaseManager:
    """Enhanced database manager with historical tracking and analytics."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database manager."""
        if db_path is None:
            db_path = Path.home() / ".arr-score-exporter" / "library.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_database()
    
    def _get_connection(self):
        """Get a database connection with proper settings for concurrency."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA busy_timeout = 30000")  # 30 second timeout
        conn.execute("PRAGMA journal_mode = WAL")     # Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA synchronous = NORMAL")   # Balance between safety and performance
        return conn
    
    def _init_database(self):
        """Initialize database schema."""
        with self._lock:
            with self._get_connection() as conn:
                conn.executescript("""
                -- Media files with comprehensive metadata
                CREATE TABLE IF NOT EXISTS media_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unique_identifier TEXT UNIQUE NOT NULL,
                    file_id INTEGER NOT NULL,
                    relative_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    total_score INTEGER NOT NULL,
                    custom_formats_json TEXT,
                    quality_profile_id INTEGER,
                    quality_profile_name TEXT,
                    quality TEXT,
                    codec TEXT,
                    resolution TEXT,
                    size_bytes INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_modified_at TIMESTAMP,
                    service_type TEXT NOT NULL,
                    movie_id INTEGER,
                    imdb_id TEXT,
                    tmdb_id INTEGER,
                    series_id INTEGER,
                    season_number INTEGER,
                    episode_number INTEGER,
                    episode_title TEXT,
                    tvdb_id INTEGER
                );
                
                -- Score history for trend analysis
                CREATE TABLE IF NOT EXISTS score_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unique_identifier TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_score INTEGER NOT NULL,
                    previous_score INTEGER,
                    change_type TEXT NOT NULL,
                    custom_formats_json TEXT,
                    notes TEXT,
                    FOREIGN KEY (unique_identifier) REFERENCES media_files (unique_identifier)
                );
                
                -- Library statistics snapshots
                CREATE TABLE IF NOT EXISTS library_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    service_type TEXT NOT NULL,
                    total_files INTEGER NOT NULL,
                    files_with_positive_scores INTEGER NOT NULL,
                    files_with_negative_scores INTEGER NOT NULL,
                    files_with_zero_scores INTEGER NOT NULL,
                    min_score INTEGER NOT NULL,
                    max_score INTEGER NOT NULL,
                    avg_score REAL NOT NULL,
                    median_score REAL NOT NULL,
                    quality_profiles_json TEXT,
                    most_common_formats_json TEXT,
                    total_size_gb REAL,
                    avg_file_size_gb REAL,
                    resolution_distribution_json TEXT,
                    codec_distribution_json TEXT
                );
                
                -- Export runs for tracking when data was collected
                CREATE TABLE IF NOT EXISTS export_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    service_type TEXT NOT NULL,
                    files_processed INTEGER NOT NULL,
                    files_added INTEGER NOT NULL,
                    files_updated INTEGER NOT NULL,
                    files_removed INTEGER NOT NULL,
                    duration_seconds REAL,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_media_files_service_type ON media_files (service_type);
                CREATE INDEX IF NOT EXISTS idx_media_files_recorded_at ON media_files (recorded_at);
                CREATE INDEX IF NOT EXISTS idx_media_files_total_score ON media_files (total_score);
                CREATE INDEX IF NOT EXISTS idx_score_history_timestamp ON score_history (timestamp);
                CREATE INDEX IF NOT EXISTS idx_score_history_change_type ON score_history (change_type);
                CREATE INDEX IF NOT EXISTS idx_library_stats_timestamp ON library_stats (timestamp);
                CREATE INDEX IF NOT EXISTS idx_export_runs_timestamp ON export_runs (timestamp);
            """)
    
    def store_media_file(self, media_file: MediaFile) -> bool:
        """Store or update a media file record."""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self._lock:
                    with self._get_connection() as conn:
                        # For Radarr/Sonarr, clean up old file records for the same movie/episode when a new file is detected
                        self._cleanup_old_file_records(conn, media_file)
                        
                        # Check if file already exists
                        existing = conn.execute(
                            "SELECT total_score FROM media_files WHERE unique_identifier = ?",
                            (media_file.unique_identifier,)
                        ).fetchone()
                        
                        custom_formats_json = json.dumps([cf.__dict__ for cf in media_file.custom_formats])
                        
                        if existing:
                            # Update existing record
                            previous_score = existing[0]
                            change_type = self._determine_change_type(previous_score, media_file.total_score)
                            
                            conn.execute("""
                                UPDATE media_files SET
                                    file_id = ?, relative_path = ?, title = ?, total_score = ?,
                                    custom_formats_json = ?, quality_profile_id = ?, quality_profile_name = ?,
                                    quality = ?, codec = ?, resolution = ?, size_bytes = ?,
                                    recorded_at = ?, file_modified_at = ?, service_type = ?,
                                    movie_id = ?, imdb_id = ?, tmdb_id = ?, series_id = ?,
                                    season_number = ?, episode_number = ?, episode_title = ?, tvdb_id = ?
                                WHERE unique_identifier = ?
                            """, (
                                media_file.file_id, media_file.relative_path, media_file.title,
                                media_file.total_score, custom_formats_json, media_file.quality_profile_id,
                                media_file.quality_profile_name, media_file.quality, media_file.codec,
                                media_file.resolution, media_file.size_bytes, media_file.recorded_at,
                                media_file.file_modified_at, media_file.service_type, media_file.movie_id,
                                media_file.imdb_id, media_file.tmdb_id, media_file.series_id,
                                media_file.season_number, media_file.episode_number, media_file.episode_title,
                                media_file.tvdb_id, media_file.unique_identifier
                            ))
                            
                            # Record score history if score changed
                            if change_type != ScoreChangeType.UNCHANGED:
                                self._record_score_history(
                                    conn, media_file.unique_identifier, media_file.total_score,
                                    previous_score, change_type, custom_formats_json
                                )
                        else:
                            # Insert new record
                            conn.execute("""
                                INSERT INTO media_files (
                                    unique_identifier, file_id, relative_path, title, total_score,
                                    custom_formats_json, quality_profile_id, quality_profile_name,
                                    quality, codec, resolution, size_bytes, recorded_at, file_modified_at,
                                    service_type, movie_id, imdb_id, tmdb_id, series_id,
                                    season_number, episode_number, episode_title, tvdb_id
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                media_file.unique_identifier, media_file.file_id, media_file.relative_path,
                                media_file.title, media_file.total_score, custom_formats_json,
                                media_file.quality_profile_id, media_file.quality_profile_name,
                                media_file.quality, media_file.codec, media_file.resolution,
                                media_file.size_bytes, media_file.recorded_at, media_file.file_modified_at,
                                media_file.service_type, media_file.movie_id, media_file.imdb_id,
                                media_file.tmdb_id, media_file.series_id, media_file.season_number,
                                media_file.episode_number, media_file.episode_title, media_file.tvdb_id
                            ))
                            
                            # Record as new file in history
                            self._record_score_history(
                                conn, media_file.unique_identifier, media_file.total_score,
                                None, ScoreChangeType.NEW_FILE, custom_formats_json
                            )
                        
                        return True
                        
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    print(f"Database lock error after {max_retries} attempts: {e}")
                    return False
            except Exception as e:
                print(f"Error storing media file: {e}")
                return False
        
        return False  # If all retries failed
    
    def store_media_files_batch(self, media_files: List[MediaFile]) -> bool:
        """Store multiple media files in a single transaction for better performance."""
        if not media_files:
            return True
            
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self._lock:
                    with self._get_connection() as conn:
                        # Use a single transaction for all files
                        conn.execute("BEGIN TRANSACTION")
                        
                        processed = 0
                        for media_file in media_files:
                            try:
                                # For Radarr/Sonarr, clean up old file records for the same movie/episode when a new file is detected
                                self._cleanup_old_file_records(conn, media_file)
                                
                                # Check if file already exists
                                existing = conn.execute(
                                    "SELECT total_score FROM media_files WHERE unique_identifier = ?",
                                    (media_file.unique_identifier,)
                                ).fetchone()
                                
                                custom_formats_json = json.dumps([cf.__dict__ for cf in media_file.custom_formats])
                                
                                if existing:
                                    # Update existing record
                                    previous_score = existing[0]
                                    change_type = self._determine_change_type(previous_score, media_file.total_score)
                                    
                                    conn.execute("""
                                        UPDATE media_files SET
                                            file_id = ?, relative_path = ?, title = ?, total_score = ?,
                                            custom_formats_json = ?, quality_profile_id = ?, quality_profile_name = ?,
                                            quality = ?, codec = ?, resolution = ?, size_bytes = ?,
                                            recorded_at = ?, file_modified_at = ?, service_type = ?,
                                            movie_id = ?, imdb_id = ?, tmdb_id = ?, series_id = ?,
                                            season_number = ?, episode_number = ?, episode_title = ?, tvdb_id = ?
                                        WHERE unique_identifier = ?
                                    """, (
                                        media_file.file_id, media_file.relative_path, media_file.title,
                                        media_file.total_score, custom_formats_json, media_file.quality_profile_id,
                                        media_file.quality_profile_name, media_file.quality, media_file.codec,
                                        media_file.resolution, media_file.size_bytes, media_file.recorded_at,
                                        media_file.file_modified_at, media_file.service_type, media_file.movie_id,
                                        media_file.imdb_id, media_file.tmdb_id, media_file.series_id,
                                        media_file.season_number, media_file.episode_number, media_file.episode_title,
                                        media_file.tvdb_id, media_file.unique_identifier
                                    ))
                                    
                                    # Record score history if score changed
                                    if change_type != ScoreChangeType.UNCHANGED:
                                        self._record_score_history(
                                            conn, media_file.unique_identifier, media_file.total_score,
                                            previous_score, change_type, custom_formats_json
                                        )
                                else:
                                    # Insert new record
                                    conn.execute("""
                                        INSERT INTO media_files (
                                            unique_identifier, file_id, relative_path, title, total_score,
                                            custom_formats_json, quality_profile_id, quality_profile_name,
                                            quality, codec, resolution, size_bytes, recorded_at, file_modified_at,
                                            service_type, movie_id, imdb_id, tmdb_id, series_id,
                                            season_number, episode_number, episode_title, tvdb_id
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        media_file.unique_identifier, media_file.file_id, media_file.relative_path,
                                        media_file.title, media_file.total_score, custom_formats_json,
                                        media_file.quality_profile_id, media_file.quality_profile_name,
                                        media_file.quality, media_file.codec, media_file.resolution,
                                        media_file.size_bytes, media_file.recorded_at, media_file.file_modified_at,
                                        media_file.service_type, media_file.movie_id, media_file.imdb_id,
                                        media_file.tmdb_id, media_file.series_id, media_file.season_number,
                                        media_file.episode_number, media_file.episode_title, media_file.tvdb_id
                                    ))
                                    
                                    # Record as new file in history
                                    self._record_score_history(
                                        conn, media_file.unique_identifier, media_file.total_score,
                                        None, ScoreChangeType.NEW_FILE, custom_formats_json
                                    )
                                
                                processed += 1
                                
                            except Exception as e:
                                print(f"Error processing file {media_file.unique_identifier}: {e}")
                                continue
                        
                        conn.execute("COMMIT")
                        print(f"Successfully stored {processed}/{len(media_files)} files to database")
                        return True
                        
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    print(f"Database lock error after {max_retries} attempts: {e}")
                    return False
            except Exception as e:
                print(f"Error in batch storage: {e}")
                return False
        
        return False
    
    def _cleanup_old_file_records(self, conn, media_file: MediaFile):
        """Clean up old file records for the same movie/episode when a new file is detected."""
        try:
            if media_file.service_type == "radarr" and media_file.movie_id:
                # For Radarr: Remove old file records for the same movie (different file_id)
                old_records = conn.execute("""
                    SELECT unique_identifier, file_id, title 
                    FROM media_files 
                    WHERE service_type = 'radarr' 
                    AND movie_id = ? 
                    AND file_id != ?
                """, (media_file.movie_id, media_file.file_id)).fetchall()
                
                if old_records:
                    print(f"Cleaning up {len(old_records)} old file record(s) for movie '{media_file.title}' (movie_id={media_file.movie_id})")
                    for old_record in old_records:
                        print(f"  Removing old file_id={old_record[1]} (keeping new file_id={media_file.file_id})")
                        
                        # Record the removal in history
                        self._record_score_history(
                            conn, old_record[0], 0, None, ScoreChangeType.REMOVED, 
                            json.dumps({"reason": "File upgraded/replaced"})
                        )
                    
                    # Delete old records
                    conn.execute("""
                        DELETE FROM media_files 
                        WHERE service_type = 'radarr' 
                        AND movie_id = ? 
                        AND file_id != ?
                    """, (media_file.movie_id, media_file.file_id))
                    
            elif media_file.service_type == "sonarr" and media_file.series_id and media_file.season_number and media_file.episode_number:
                # For Sonarr: Remove old file records for the same episode (different file_id)
                old_records = conn.execute("""
                    SELECT unique_identifier, file_id, title 
                    FROM media_files 
                    WHERE service_type = 'sonarr' 
                    AND series_id = ? 
                    AND season_number = ? 
                    AND episode_number = ? 
                    AND file_id != ?
                """, (media_file.series_id, media_file.season_number, media_file.episode_number, media_file.file_id)).fetchall()
                
                if old_records:
                    print(f"Cleaning up {len(old_records)} old file record(s) for episode '{media_file.title}' S{media_file.season_number:02d}E{media_file.episode_number:02d}")
                    for old_record in old_records:
                        print(f"  Removing old file_id={old_record[1]} (keeping new file_id={media_file.file_id})")
                        
                        # Record the removal in history
                        self._record_score_history(
                            conn, old_record[0], 0, None, ScoreChangeType.REMOVED, 
                            json.dumps({"reason": "File upgraded/replaced"})
                        )
                    
                    # Delete old records
                    conn.execute("""
                        DELETE FROM media_files 
                        WHERE service_type = 'sonarr' 
                        AND series_id = ? 
                        AND season_number = ? 
                        AND episode_number = ? 
                        AND file_id != ?
                    """, (media_file.series_id, media_file.season_number, media_file.episode_number, media_file.file_id))
                    
        except Exception as e:
            print(f"Warning: Error during old file cleanup: {e}")
            # Don't fail the entire operation if cleanup fails

    def _determine_change_type(self, old_score: int, new_score: int) -> ScoreChangeType:
        """Determine the type of score change."""
        if new_score > old_score:
            return ScoreChangeType.IMPROVED
        elif new_score < old_score:
            return ScoreChangeType.DEGRADED
        else:
            return ScoreChangeType.UNCHANGED
    
    def _record_score_history(self, conn, unique_id: str, new_score: int, old_score: Optional[int],
                            change_type: ScoreChangeType, custom_formats_json: str):
        """Record score change in history."""
        conn.execute("""
            INSERT INTO score_history (
                unique_identifier, total_score, previous_score, change_type, custom_formats_json
            ) VALUES (?, ?, ?, ?, ?)
        """, (unique_id, new_score, old_score, change_type.value, custom_formats_json))
    
    def get_upgrade_candidates(self, min_score: int = 50, service_type: Optional[str] = None) -> List[MediaFile]:
        """Get files that are candidates for upgrade based on low scores."""
        query = """
            SELECT * FROM media_files
            WHERE total_score <= ?
        """
        params = [min_score]
        
        if service_type:
            query += " AND service_type = ?"
            params.append(service_type)
        
        query += " ORDER BY total_score ASC, title ASC"
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        
        return [self._row_to_media_file(row) for row in rows]
    
    def get_files_with_size_data(self, service_type: Optional[str] = None, limit: int = 100) -> List[MediaFile]:
        """Get files that have size data for scatter plot visualization."""
        query = """
            SELECT * FROM media_files
            WHERE size_bytes IS NOT NULL AND size_bytes > 0
        """
        params = []
        
        if service_type:
            query += " AND service_type = ?"
            params.append(service_type)
        
        query += " ORDER BY total_score DESC, size_bytes DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        
        return [self._row_to_media_file(row) for row in rows]
    
    def get_score_trends(self, days: int = 30, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get score trends over time."""
        query = """
            SELECT h.*, m.title, m.service_type
            FROM score_history h
            JOIN media_files m ON h.unique_identifier = m.unique_identifier
            WHERE h.timestamp >= datetime('now', '-{} days')
            AND h.change_type IN ('improved', 'degraded')
        """.format(days)
        
        params = []
        if service_type:
            query += " AND m.service_type = ?"
            params.append(service_type)
        
        query += " ORDER BY h.timestamp DESC"
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        
        return [dict(row) for row in rows]
    
    def calculate_library_stats(self, service_type: str) -> LibraryStats:
        """Calculate comprehensive library statistics."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            # Basic counts and score statistics
            stats_row = conn.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(CASE WHEN total_score > 0 THEN 1 ELSE 0 END) as positive_scores,
                    SUM(CASE WHEN total_score < 0 THEN 1 ELSE 0 END) as negative_scores,
                    SUM(CASE WHEN total_score = 0 THEN 1 ELSE 0 END) as zero_scores,
                    MIN(total_score) as min_score,
                    MAX(total_score) as max_score,
                    AVG(total_score) as avg_score,
                    SUM(size_bytes) as total_bytes
                FROM media_files
                WHERE service_type = ?
            """, (service_type,)).fetchone()
            
            # Quality profile distribution
            profile_rows = conn.execute("""
                SELECT quality_profile_name, COUNT(*) as count
                FROM media_files
                WHERE service_type = ? AND quality_profile_name IS NOT NULL
                GROUP BY quality_profile_name
                ORDER BY count DESC
            """, (service_type,)).fetchall()
            
            # Resolution distribution
            resolution_rows = conn.execute("""
                SELECT resolution, COUNT(*) as count
                FROM media_files
                WHERE service_type = ? AND resolution IS NOT NULL
                GROUP BY resolution
                ORDER BY count DESC
            """, (service_type,)).fetchall()
            
            # Codec distribution
            codec_rows = conn.execute("""
                SELECT codec, COUNT(*) as count
                FROM media_files
                WHERE service_type = ? AND codec IS NOT NULL
                GROUP BY codec
                ORDER BY count DESC
            """, (service_type,)).fetchall()
            
            # Median score calculation
            median_row = conn.execute("""
                SELECT total_score
                FROM (
                    SELECT total_score, ROW_NUMBER() OVER (ORDER BY total_score) as rn,
                           COUNT(*) OVER () as total_count
                    FROM media_files
                    WHERE service_type = ?
                )
                WHERE rn IN ((total_count + 1) / 2, (total_count + 2) / 2)
            """, (service_type,)).fetchall()
            
            median_score = sum(row[0] for row in median_row) / len(median_row) if median_row else 0
            
        return LibraryStats(
            timestamp=datetime.datetime.now(),
            service_type=service_type,
            total_files=stats_row['total_files'],
            files_with_positive_scores=stats_row['positive_scores'],
            files_with_negative_scores=stats_row['negative_scores'],
            files_with_zero_scores=stats_row['zero_scores'],
            min_score=stats_row['min_score'] or 0,
            max_score=stats_row['max_score'] or 0,
            avg_score=stats_row['avg_score'] or 0,
            median_score=median_score,
            quality_profiles={row['quality_profile_name']: row['count'] for row in profile_rows},
            most_common_formats=[],  # TODO: Implement format analysis
            total_size_gb=(stats_row['total_bytes'] or 0) / (1024**3),
            avg_file_size_gb=((stats_row['total_bytes'] or 0) / (1024**3)) / max(stats_row['total_files'], 1),
            resolution_distribution={row['resolution']: row['count'] for row in resolution_rows},
            codec_distribution={row['codec']: row['count'] for row in codec_rows}
        )
    
    def _row_to_media_file(self, row: sqlite3.Row) -> MediaFile:
        """Convert database row to MediaFile object."""
        custom_formats = []
        if row['custom_formats_json']:
            try:
                formats_data = json.loads(row['custom_formats_json'])
                custom_formats = [
                    CustomFormatDetail(
                        name=cf['name'],
                        score=cf['score'],
                        format_id=cf['format_id'],
                        category=cf.get('category'),
                        tags=cf.get('tags', [])
                    )
                    for cf in formats_data
                ]
            except (json.JSONDecodeError, KeyError):
                pass
        
        return MediaFile(
            file_id=row['file_id'],
            relative_path=row['relative_path'],
            title=row['title'],
            total_score=row['total_score'],
            custom_formats=custom_formats,
            quality_profile_id=row['quality_profile_id'],
            quality_profile_name=row['quality_profile_name'] or "",
            quality=row['quality'],
            codec=row['codec'],
            resolution=row['resolution'],
            size_bytes=row['size_bytes'],
            recorded_at=datetime.datetime.fromisoformat(row['recorded_at']),
            file_modified_at=datetime.datetime.fromisoformat(row['file_modified_at']) if row['file_modified_at'] else None,
            service_type=row['service_type'],
            movie_id=row['movie_id'],
            imdb_id=row['imdb_id'],
            tmdb_id=row['tmdb_id'],
            series_id=row['series_id'],
            season_number=row['season_number'],
            episode_number=row['episode_number'],
            episode_title=row['episode_title'],
            tvdb_id=row['tvdb_id']
        )
    
    def get_zero_score_files(self, service_type: str, limit: Optional[int] = None) -> List[MediaFile]:
        """
        Get all files with zero scores for analysis and display.
        
        Args:
            service_type: Type of service ('radarr' or 'sonarr')
            limit: Optional limit on number of files to return
            
        Returns:
            List of MediaFile objects with zero scores
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT * FROM media_files 
                WHERE service_type = ? AND total_score = 0
                ORDER BY recorded_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            rows = conn.execute(query, (service_type,)).fetchall()
            return [self._row_to_media_file(row) for row in rows]