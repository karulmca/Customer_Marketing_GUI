"""
Configuration Loader for Company Data Scraper
Centralized configuration management from config.json
"""

import os
import json
import sys
from typing import Dict, Any, Optional

class ConfigLoader:
    """Loads and manages configuration from config.json"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Default to config.json in project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_file = os.path.join(project_root, "config.json")
        
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            # First try the main config file
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ Configuration loaded from: {self.config_file}")
                    return config
            
            # Try production config as fallback
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            production_config = os.path.join(project_root, "config.production.json")
            
            if os.path.exists(production_config):
                with open(production_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ Production configuration loaded from: {production_config}")
                    return config
            
            print(f"⚠️ Config files not found: {self.config_file}, {production_config}")
            print("Using default configuration")
            return self._get_default_config()
                
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file is not found"""
        return {
            "scheduler_settings": {
                "interval_minutes": 2,
                "max_concurrent_jobs_per_user": 1,
                "job_timeout_minutes": 30,
                "retry_failed_jobs": True,
                "max_retries": 3,
                "cleanup_completed_jobs_days": 7
            },
            "job_processing": {
                "single_job_per_user": True,
                "queue_priority": "first_in_first_out",
                "auto_start_processing": True,
                "max_processing_time_minutes": 60
            }
        }
    
    def get_scheduler_interval(self) -> int:
        """Get scheduler interval in minutes"""
        return self._config.get("scheduler_settings", {}).get("interval_minutes", 2)

    def set_scheduler_interval(self, minutes: int) -> bool:
        """Set scheduler interval (minutes) and persist to config file if writable."""
        try:
            minutes = int(minutes)
            if minutes < 1:
                raise ValueError("Interval must be >= 1 minute")
            if "scheduler_settings" not in self._config:
                self._config["scheduler_settings"] = {}
            self._config["scheduler_settings"]["interval_minutes"] = minutes
            # Try to persist back to the config file if possible
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2)
                    print(f"✅ Persisted scheduler interval ({minutes} min) to {self.config_file}")
            except Exception:
                # If we cannot write the config, still update the in-memory config
                print(f"⚠️ Unable to persist config to {self.config_file}; using in-memory value only")
            return True
        except Exception as e:
            print(f"❌ Failed to set scheduler interval: {e}")
            return False
    
    def get_max_concurrent_jobs_per_user(self) -> int:
        """Get maximum concurrent jobs per user"""
        return self._config.get("scheduler_settings", {}).get("max_concurrent_jobs_per_user", 1)
    
    def get_job_timeout_minutes(self) -> int:
        """Get job timeout in minutes"""
        return self._config.get("scheduler_settings", {}).get("job_timeout_minutes", 30)
    
    def is_single_job_per_user_enabled(self) -> bool:
        """Check if single job per user is enabled"""
        return self._config.get("job_processing", {}).get("single_job_per_user", True)
    
    def get_max_retries(self) -> int:
        """Get maximum retry count for failed jobs"""
        return self._config.get("scheduler_settings", {}).get("max_retries", 3)
    
    def is_retry_failed_jobs_enabled(self) -> bool:
        """Check if retry failed jobs is enabled"""
        return self._config.get("scheduler_settings", {}).get("retry_failed_jobs", True)
    
    def get_queue_priority(self) -> str:
        """Get queue priority strategy"""
        return self._config.get("job_processing", {}).get("queue_priority", "first_in_first_out")
    
    def is_auto_start_processing_enabled(self) -> bool:
        """Check if auto start processing is enabled"""
        return self._config.get("job_processing", {}).get("auto_start_processing", True)
    
    def get_max_processing_time_minutes(self) -> int:
        """Get maximum processing time in minutes"""
        return self._config.get("job_processing", {}).get("max_processing_time_minutes", 60)
    
    def get_cleanup_completed_jobs_days(self) -> int:
        """Get cleanup period for completed jobs in days"""
        return self._config.get("scheduler_settings", {}).get("cleanup_completed_jobs_days", 7)
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary"""
        return self._config.copy()
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a specific configuration section"""
        return self._config.get(section_name, {})
    
    def reload_config(self) -> bool:
        """Reload configuration from file"""
        try:
            self._config = self._load_config()
            print("✅ Configuration reloaded successfully")
            return True
        except Exception as e:
            print(f"❌ Error reloading config: {e}")
            return False

# Global configuration instance
config = ConfigLoader()

# Convenience functions for common config access
def get_scheduler_interval() -> int:
    """Get scheduler interval in minutes"""
    return config.get_scheduler_interval()

def set_scheduler_interval(minutes: int) -> bool:
    """Set scheduler interval and persist it via the global config instance."""
    return config.set_scheduler_interval(minutes)

def get_max_concurrent_jobs_per_user() -> int:
    """Get maximum concurrent jobs per user"""
    return config.get_max_concurrent_jobs_per_user()

def is_single_job_per_user_enabled() -> bool:
    """Check if single job per user is enabled"""
    return config.is_single_job_per_user_enabled()

def get_job_timeout_minutes() -> int:
    """Get job timeout in minutes"""
    return config.get_job_timeout_minutes()

def get_max_retries() -> int:
    """Get maximum retry count for failed jobs"""
    return config.get_max_retries()