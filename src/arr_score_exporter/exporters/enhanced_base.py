"""
Enhanced base exporter with performance optimizations, caching, and advanced features.

This next-generation exporter provides:
- Intelligent caching with TTL
- Advanced concurrency with rate limiting  
- Rich metadata extraction
- Historical tracking integration
- Real-time progress reporting
- Comprehensive error handling and retry logic
"""

import asyncio
import time
import json
import hashlib
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models import MediaFile, CustomFormatDetail, DatabaseManager
from ..analysis import IntelligentAnalyzer
from ..reporting import HTMLReporter


@dataclass
class ExportConfig:
    """Enhanced configuration for exporters."""
    # Connection settings
    api_key: str
    url: str
    timeout: int = 30
    
    # Performance settings
    max_workers: int = 20
    rate_limit_per_second: float = 10.0
    request_delay: float = 0.1
    
    # Caching settings
    cache_enabled: bool = True
    cache_ttl_minutes: int = 60
    cache_dir: Optional[Path] = None
    
    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ['csv', 'json'])
    generate_html_report: bool = True
    store_in_database: bool = True
    
    # Analysis settings
    enable_analysis: bool = True
    identify_upgrade_candidates: bool = True
    min_upgrade_score_threshold: int = -50


@dataclass
class ProgressInfo:
    """Real-time progress information."""
    total_items: int
    processed_items: int
    current_phase: str
    start_time: datetime
    errors: int = 0
    
    @property
    def percentage(self) -> float:
        return (self.processed_items / max(self.total_items, 1)) * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        return datetime.now() - self.start_time
    
    @property
    def estimated_time_remaining(self) -> Optional[timedelta]:
        if self.processed_items == 0:
            return None
        rate = self.processed_items / self.elapsed_time.total_seconds()
        remaining_items = self.total_items - self.processed_items
        return timedelta(seconds=remaining_items / rate)


class CacheManager:
    """Intelligent caching system with TTL and compression."""
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_minutes: int = 60):
        if cache_dir is None:
            cache_dir = Path.home() / ".arr-score-exporter" / "cache"
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(minutes=ttl_minutes)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key from URL and parameters."""
        content = f"{url}#{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Get cached response if valid."""
        try:
            cache_key = self._get_cache_key(url, params)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check TTL
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_file.unlink()  # Remove expired cache
                return None
            
            self.logger.debug(f"Cache hit for {url}")
            return cached_data['data']
            
        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")
            return None
    
    def set(self, url: str, data: Dict, params: Dict = None):
        """Cache response data."""
        try:
            cache_key = self._get_cache_key(url, params)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'params': params,
                'data': data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")
    
    def clear_expired(self):
        """Remove expired cache entries."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cached_time > self.ttl:
                        cache_file.unlink()
                        
                except Exception:
                    # Remove corrupted cache files
                    cache_file.unlink()
                    
        except Exception as e:
            self.logger.warning(f"Cache cleanup error: {e}")


class RateLimiter:
    """Rate limiter with token bucket algorithm."""
    
    def __init__(self, rate_per_second: float):
        self.rate = rate_per_second
        self.tokens = rate_per_second
        self.last_update = time.time()
        self.lock = asyncio.Lock() if asyncio.iscoroutinefunction(self.__init__) else None
    
    def acquire(self):
        """Acquire permission to make a request."""
        now = time.time()
        time_passed = now - self.last_update
        self.last_update = now
        
        # Add tokens based on time passed
        self.tokens = min(self.rate, self.tokens + time_passed * self.rate)
        
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        else:
            # Wait for next token
            wait_time = (1.0 - self.tokens) / self.rate
            time.sleep(wait_time)
            self.tokens = 0.0
            return True


class EnhancedApiClient:
    """High-performance API client with caching, rate limiting, and retry logic."""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session()
        self.cache = CacheManager(config.cache_dir, config.cache_ttl_minutes) if config.cache_enabled else None
        self.rate_limiter = RateLimiter(config.rate_limit_per_second)
        
        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _create_session(self) -> requests.Session:
        """Create optimized requests session."""
        session = requests.Session()
        
        # Aggressive retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,
            pool_maxsize=20,
            pool_block=True
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Optimized headers
        session.headers.update({
            'X-Api-Key': self.config.api_key,
            'User-Agent': 'arr-score-exporter/2.0 (Enhanced)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None, 
                    use_cache: bool = True) -> Optional[Dict]:
        """Make API request with caching and rate limiting."""
        url = f"{self.config.url.rstrip('/')}{endpoint}"
        
        # Check cache first
        if use_cache and self.cache:
            cached_result = self.cache.get(url, params)
            if cached_result is not None:
                self.cache_hits += 1
                return cached_result
            self.cache_misses += 1
        
        # Rate limiting
        self.rate_limiter.acquire()
        
        try:
            # Add artificial delay if configured
            if self.config.request_delay > 0:
                time.sleep(self.config.request_delay)
            
            self.request_count += 1
            response = self.session.get(
                url, 
                params=params or {}, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Cache successful responses
            if use_cache and self.cache and response.status_code == 200:
                self.cache.set(url, data, params)
            
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout connecting to {url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                self.logger.error(f"HTTP Error {e.response.status_code} for {url}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON response from {url}")
        
        return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'requests_made': self.request_count,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': self.cache_hits / max(self.cache_hits + self.cache_misses, 1) * 100
        }
    
    def close(self):
        """Close session and cleanup."""
        self.session.close()
        if self.cache:
            self.cache.clear_expired()


class EnhancedBaseExporter(ABC):
    """Next-generation base exporter with advanced features."""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        self.client = EnhancedApiClient(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.progress = None
        
        # Initialize components
        self.db_manager = DatabaseManager() if config.store_in_database else None
        self.analyzer = IntelligentAnalyzer(self.db_manager) if config.enable_analysis and self.db_manager else None
        self.html_reporter = HTMLReporter() if config.generate_html_report else None
        
        # Cache quality profiles
        self.quality_profiles: Dict[int, str] = {}
        self._load_quality_profiles()
    
    def _load_quality_profiles(self):
        """Load and cache quality profile mappings."""
        self.logger.info("Loading quality profiles...")
        profiles = self.client.make_request("/api/v3/qualityprofile")
        
        if profiles:
            self.quality_profiles = {
                p['id']: p['name'] for p in profiles 
                if 'id' in p and 'name' in p
            }
            self.logger.info(f"Loaded {len(self.quality_profiles)} quality profiles")
        else:
            self.logger.error("Failed to load quality profiles")
    
    @abstractmethod
    def get_service_type(self) -> str:
        """Get service type identifier (radarr/sonarr)."""
        pass
    
    @abstractmethod
    def collect_items(self) -> List[Tuple[Dict, int]]:
        """Collect items and their file IDs for processing."""
        pass
    
    @abstractmethod
    def fetch_file_details(self, file_id: int) -> Optional[Dict]:
        """Fetch detailed information for a single file."""
        pass
    
    @abstractmethod
    def create_media_file(self, item_info: Dict, file_details: Dict) -> MediaFile:
        """Create MediaFile object from item info and file details."""
        pass
    
    def extract_custom_formats(self, file_details: Dict) -> List[CustomFormatDetail]:
        """Extract custom format details from file data."""
        formats = []
        custom_formats_list = file_details.get("customFormats", [])
        
        if isinstance(custom_formats_list, list):
            for cf in custom_formats_list:
                if isinstance(cf, dict):
                    formats.append(CustomFormatDetail(
                        name=cf.get("name", "Unknown"),
                        score=cf.get("score", 0),
                        format_id=cf.get("id", 0),
                        category=cf.get("category"),
                        tags=cf.get("tags", [])
                    ))
        
        return formats
    
    def calculate_total_score(self, file_details: Dict) -> int:
        """Calculate total custom format score."""
        # Try direct score first
        score = file_details.get("customFormatScore", 0)
        
        # Fallback to summing individual format scores
        if score == 0:
            custom_formats = self.extract_custom_formats(file_details)
            score = sum(cf.score for cf in custom_formats)
        
        return score
    
    def fetch_files_parallel(self, file_ids: List[int]) -> Dict[int, Dict]:
        """Fetch file details in parallel with progress tracking."""
        self.logger.info(f"Fetching details for {len(file_ids)} files using {self.config.max_workers} workers")
        
        if self.progress:
            self.progress.current_phase = "Fetching file details"
            self.progress.total_items = len(file_ids)
            self.progress.processed_items = 0
        
        file_details = {}
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_id = {
                executor.submit(self.fetch_file_details, file_id): file_id 
                for file_id in file_ids
            }
            
            for future in as_completed(future_to_id):
                file_id = future_to_id[future]
                try:
                    details = future.result()
                    if details:
                        file_details[file_id] = details
                except Exception as e:
                    self.logger.warning(f"Error fetching file {file_id}: {e}")
                    if self.progress:
                        self.progress.errors += 1
                
                if self.progress:
                    self.progress.processed_items += 1
                    if self.progress.processed_items % 25 == 0:
                        self.logger.info(
                            f"Progress: {self.progress.percentage:.1f}% "
                            f"({self.progress.processed_items}/{self.progress.total_items})"
                        )
        
        return file_details
    
    def export(self) -> bool:
        """Enhanced export process with full feature set."""
        start_time = datetime.now()
        self.logger.info(f"Starting enhanced {self.get_service_type()} export...")
        
        try:
            # Initialize progress tracking
            self.progress = ProgressInfo(
                total_items=0,
                processed_items=0,
                current_phase="Initializing",
                start_time=start_time
            )
            
            # Phase 1: Collect items
            self.progress.current_phase = "Collecting items"
            self.logger.info("Collecting items...")
            items = self.collect_items()
            
            if not items:
                self.logger.info("No items found to process")
                return True
            
            # Phase 2: Fetch file details
            file_ids = [file_id for _, file_id in items]
            file_details = self.fetch_files_parallel(file_ids)
            
            # Phase 3: Process and store data
            self.progress.current_phase = "Processing results"
            self.progress.total_items = len(items)
            self.progress.processed_items = 0
            
            media_files = []
            for item_info, file_id in items:
                details = file_details.get(file_id)
                if details:
                    try:
                        media_file = self.create_media_file(item_info, details)
                        media_files.append(media_file)
                        
                        # Store in database if enabled
                        if self.db_manager:
                            self.db_manager.store_media_file(media_file)
                            
                    except Exception as e:
                        self.logger.warning(f"Error processing file {file_id}: {e}")
                        if self.progress:
                            self.progress.errors += 1
                
                if self.progress:
                    self.progress.processed_items += 1
            
            # Phase 4: Generate outputs
            self.progress.current_phase = "Generating outputs"
            self._generate_outputs(media_files)
            
            # Phase 5: Generate analysis and reports
            if self.config.enable_analysis and self.analyzer:
                self.progress.current_phase = "Generating analysis"
                self._generate_analysis_reports()
            
            # Log performance stats
            stats = self.client.get_performance_stats()
            duration = datetime.now() - start_time
            
            self.logger.info(f"Export completed successfully in {duration}")
            self.logger.info(f"Performance: {stats['requests_made']} requests, "
                           f"{stats['cache_hit_rate']:.1f}% cache hit rate")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False
        finally:
            self.client.close()
    
    def _generate_outputs(self, media_files: List[MediaFile]):
        """Generate output files in requested formats."""
        if not media_files:
            self.logger.info("No data to export")
            return
        
        service_type = self.get_service_type()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV output
        if 'csv' in self.config.output_formats:
            csv_path = Path(f"{service_type}_scores_{timestamp}.csv")
            self._write_csv(media_files, csv_path)
        
        # JSON output
        if 'json' in self.config.output_formats:
            json_path = Path(f"{service_type}_scores_{timestamp}.json")
            self._write_json(media_files, json_path)
    
    def _write_csv(self, media_files: List[MediaFile], output_path: Path):
        """Write enhanced CSV with rich metadata."""
        import csv
        
        fieldnames = self._get_csv_fieldnames()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for media_file in media_files:
                row = self._media_file_to_csv_row(media_file)
                writer.writerow(row)
        
        self.logger.info(f"Wrote {len(media_files)} entries to {output_path}")
    
    def _write_json(self, media_files: List[MediaFile], output_path: Path):
        """Write JSON output with full metadata."""
        data = {
            'export_info': {
                'service_type': self.get_service_type(),
                'exported_at': datetime.now().isoformat(),
                'total_files': len(media_files),
                'exporter_version': '2.0'
            },
            'files': [media_file.to_dict() for media_file in media_files]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Wrote JSON data to {output_path}")
    
    def _generate_analysis_reports(self):
        """Generate intelligent analysis and HTML reports."""
        if not self.analyzer:
            return
        
        service_type = self.get_service_type()
        
        try:
            # Generate health report
            health_report = self.analyzer.generate_library_health_report(service_type)
            library_stats = self.analyzer.db.calculate_library_stats(service_type)
            
            # Generate HTML report
            if self.html_reporter:
                html_path = self.html_reporter.generate_library_health_report(
                    health_report, library_stats
                )
                self.logger.info(f"Generated health report: {html_path}")
            
            # Log key insights
            self.logger.info(f"Library Health Score: {health_report.health_score:.1f}/100 ({health_report.health_grade})")
            self.logger.info(f"Upgrade Candidates: {len(health_report.upgrade_candidates)}")
            
            if health_report.achievements:
                self.logger.info("Achievements: " + "; ".join(health_report.achievements[:3]))
            
            if health_report.warnings:
                self.logger.warning("Warnings: " + "; ".join(health_report.warnings[:3]))
                
        except Exception as e:
            self.logger.error(f"Error generating analysis: {e}")
    
    @abstractmethod
    def _get_csv_fieldnames(self) -> List[str]:
        """Get CSV column names."""
        pass
    
    @abstractmethod
    def _media_file_to_csv_row(self, media_file: MediaFile) -> Dict[str, Any]:
        """Convert MediaFile to CSV row."""
        pass