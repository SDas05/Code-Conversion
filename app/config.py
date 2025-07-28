import json
from pathlib import Path
from typing import Any


class ConfigLoader:
    """
    Loads and provides access to the configuration from config.json.
    Supports nested access via dot-separated keys.
    """

    def __init__(self, config_path: str = "config.json"):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_file, "r", encoding="utf-8") as f:
            self._config = json.load(f)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a nested configuration value using dot-separated key path.
        Example: get("model.model_name") returns "gpt-4"
        """
        keys = key_path.split(".")
        value = self._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def raw(self) -> dict:
        """
        Access the full raw configuration as a dictionary.
        """
        return self._config


# Singleton instance used throughout the app
config = ConfigLoader()
