"""Configuration loader implementation"""

import os
from typing import Dict, Any, Optional
import yaml
from omegaconf import OmegaConf, DictConfig
from src.common.logging_config import setup_logging, get_logger

# Setup logging
logger = setup_logging("config_loader", "DEBUG")


class ConfigLoader:
    """Singleton class for loading and managing configuration"""

    _instance = None
    _config_cache: Dict[str, DictConfig] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the config loader"""
        logger.info("Initializing ConfigLoader")
        self._config_cache = {}
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all configuration files from the config directory"""
        try:
            config_dir = os.path.join(os.getcwd(), "config")
            if not os.path.exists(config_dir):
                logger.warning(f"Config directory not found: {config_dir}")
                return

            for filename in os.listdir(config_dir):
                if filename.endswith('.yaml'):
                    config_name = filename[:-5]  # Remove .yaml extension
                    config_path = os.path.join(config_dir, filename)
                    self._load_config(config_name, config_path)

            logger.info("All configurations loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configurations: {str(e)}", exc_info=True)
            raise

    def _load_config(self, config_name: str, config_path: str):
        """Load a specific configuration file"""
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                omega_config = OmegaConf.create(yaml_config)
                self._config_cache[config_name] = omega_config
                logger.debug(f"Loaded configuration: {config_name} with values: {omega_config}")
        except Exception as e:
            logger.error(f"Error loading configuration {config_name}: {str(e)}", exc_info=True)
            raise

    def get_config(self, config_name: str) -> Optional[DictConfig]:
        """Get a specific configuration by name"""
        return self._config_cache.get(config_name)

    def get_all_configs(self) -> Dict[str, DictConfig]:
        """Get all loaded configurations"""
        return self._config_cache

    def reload_config(self, config_name: str):
        """Reload a specific configuration"""
        try:
            config_path = os.path.join(os.getcwd(), "config", f"{config_name}.yaml")
            if os.path.exists(config_path):
                self._load_config(config_name, config_path)
                logger.info(f"Configuration reloaded: {config_name}")
            else:
                logger.warning(f"Configuration file not found: {config_path}")
        except Exception as e:
            logger.error(f"Error reloading configuration {config_name}: {str(e)}", exc_info=True)
            raise

    def reload_all_configs(self):
        """Reload all configurations"""
        self._config_cache.clear()
        self._load_all_configs()
