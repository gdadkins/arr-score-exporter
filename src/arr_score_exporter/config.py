"""Configuration management for Arr Score Exporter."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        if config_path is None:
            config_path = self._find_config_file()
        
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()
    
    def _find_config_file(self) -> str:
        """Find configuration file in common locations."""
        possible_paths = [
            "config.yaml",
            "config.yml",
            os.path.expanduser("~/.arr-score-exporter/config.yaml"),
            "/etc/arr-score-exporter/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError(
            "No configuration file found. Please create config.yaml from config.yaml.example"
        )
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def radarr_url(self) -> str:
        return self.get('radarr.url', '')
    
    @property
    def radarr_api_key(self) -> str:
        return self.get('radarr.api_key', '')
    
    @property
    def sonarr_url(self) -> str:
        return self.get('sonarr.url', '')
    
    @property
    def sonarr_api_key(self) -> str:
        return self.get('sonarr.api_key', '')
    
    def is_radarr_enabled(self) -> bool:
        return self.get('radarr.enabled', False)
    
    def is_sonarr_enabled(self) -> bool:
        return self.get('sonarr.enabled', False)
