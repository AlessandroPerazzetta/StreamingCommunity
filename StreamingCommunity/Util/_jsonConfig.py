# 29.01.24

import os
import sys
import json
import logging
import requests
from typing import Any, List


# External library
from rich.console import Console


# Variable
console = Console()


class ConfigManager:
    def __init__(self, file_name: str = 'config.json') -> None:
        """Initialize the ConfigManager.

        Parameters:
            - file_name (str, optional): The name of the configuration file. Default is 'config.json'.
        """
        if getattr(sys, 'frozen', False):
            base_path = os.path.join(".")
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.file_path = os.path.join(base_path, file_name)
        self.config = {}
        self.configSite = {}
        self.cache = {}

        console.print(f"[bold cyan]📂 Configuration file path:[/bold cyan] [green]{self.file_path}[/green]")

    def read_config(self) -> None:
        """Read the configuration file."""
        try:
            logging.info(f"📖 Reading file: {self.file_path}")

            # Check if file exists
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    self.config = json.load(f)
                console.print("[bold green]✅ Configuration file loaded successfully.[/bold green]")

            else:
                console.print("[bold yellow]⚠️ Configuration file not found. Downloading...[/bold yellow]")
                self.download_requirements(
                    'https://raw.githubusercontent.com/Arrowar/StreamingCommunity/refs/heads/main/config.json',
                    self.file_path
                )

                # Load the downloaded config.json into the config attribute
                with open(self.file_path, 'r') as f:
                    self.config = json.load(f)
                console.print("[bold green]✅ Configuration file downloaded and saved.[/bold green]")

            # Update site configuration separately
            self.update_site_config()

            console.print("[bold cyan]🔧 Configuration file processing complete.[/bold cyan]")

        except Exception as e:
            logging.error(f"❌ Error reading configuration file: {e}")

    def download_requirements(self, url: str, filename: str):
        """
        Download a file from the specified URL if not found locally using requests.

        Args:
            url (str): The URL to download the file from.
            filename (str): The local filename to save the file as.
        """
        try:
            logging.info(f"🌍 Downloading {filename} from {url}...")
            response = requests.get(url)

            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                console.print(f"[bold green]✅ Successfully downloaded {filename}.[/bold green]")
                
            else:
                logging.error(f"❌ Failed to download {filename}. HTTP Status code: {response.status_code}")
                sys.exit(0)

        except Exception as e:
            logging.error(f"❌ Failed to download {filename}: {e}")
            sys.exit(0)

    def update_site_config(self) -> None:
        """Fetch and update the site configuration with data from the API."""
        api_url = "https://api.npoint.io/e67633acc3816cc70132"
        try:
            console.print("[bold cyan]🌍 Fetching SITE data from API...[/bold cyan]")
            response = requests.get(api_url)

            if response.status_code == 200:
                self.configSite = response.json()  # Store API data in separate configSite
                console.print("[bold green]✅ SITE data successfully fetched.[/bold green]")
            else:
                console.print(f"[bold red]❌ Failed to fetch SITE data. HTTP Status code: {response.status_code}[/bold red]")

        except Exception as e:
            console.print(f"[bold red]❌ Error fetching SITE data: {e}[/bold red]")

    def read_key(self, section: str, key: str, data_type: type = str, from_site: bool = False) -> Any:
        """Read a key from the configuration.

        Parameters:
            - section (str): The section in the configuration.
            - key (str): The key to be read.
            - data_type (type, optional): The expected data type of the key's value. Default is str.
            - from_site (bool, optional): Whether to read from site config. Default is False.

        Returns:
            The value of the key converted to the specified data type.
        """
        cache_key = f"{'site' if from_site else 'config'}.{section}.{key}"
        logging.info(f"Read key: {cache_key}")

        if cache_key in self.cache:
            return self.cache[cache_key]

        config_source = self.configSite if from_site else self.config
        
        if section in config_source and key in config_source[section]:
            value = config_source[section][key]
        else:
            raise ValueError(f"Key '{key}' not found in section '{section}' of {'site' if from_site else 'main'} config")

        value = self._convert_to_data_type(value, data_type)
        self.cache[cache_key] = value

        return value

    def _convert_to_data_type(self, value: str, data_type: type) -> Any:
        """Convert the value to the specified data type.

        Parameters:
            - value (str): The value to be converted.
            - data_type (type): The expected data type.

        Returns:
            The value converted to the specified data type.
        """
        if data_type == int:
            return int(value)
        elif data_type == bool:
            return bool(value)
        elif data_type == list:
            return value if isinstance(value, list) else [item.strip() for item in value.split(',')]
        elif data_type == type(None):
            return None
        else:
            return value

    # Main config getters
    def get(self, section: str, key: str) -> Any:
        """Read a value from the main configuration."""
        return self.read_key(section, key)

    def get_int(self, section: str, key: str) -> int:
        """Read an integer value from the main configuration."""
        return self.read_key(section, key, int)

    def get_float(self, section: str, key: str) -> float:
        """Read a float value from the main configuration."""
        return self.read_key(section, key, float)

    def get_bool(self, section: str, key: str) -> bool:
        """Read a boolean value from the main configuration."""
        return self.read_key(section, key, bool)

    def get_list(self, section: str, key: str) -> List[str]:
        """Read a list value from the main configuration."""
        return self.read_key(section, key, list)

    def get_dict(self, section: str, key: str) -> dict:
        """Read a dictionary value from the main configuration."""
        return self.read_key(section, key, dict)

    # Site config getters
    def get_site(self, section: str, key: str) -> Any:
        """Read a value from the site configuration."""
        return self.read_key(section, key, from_site=True)

    def get_site_int(self, section: str, key: str) -> int:
        """Read an integer value from the site configuration."""
        return self.read_key(section, key, int, from_site=True)

    def get_site_float(self, section: str, key: str) -> float:
        """Read a float value from the site configuration."""
        return self.read_key(section, key, float, from_site=True)

    def get_site_bool(self, section: str, key: str) -> bool:
        """Read a boolean value from the site configuration."""
        return self.read_key(section, key, bool, from_site=True)

    def get_site_list(self, section: str, key: str) -> List[str]:
        """Read a list value from the site configuration."""
        return self.read_key(section, key, list, from_site=True)

    def get_site_dict(self, section: str, key: str) -> dict:
        """Read a dictionary value from the site configuration."""
        return self.read_key(section, key, dict, from_site=True)

    def set_key(self, section: str, key: str, value: Any, to_site: bool = False) -> None:
        """Set a key in the configuration.

        Parameters:
            - section (str): The section in the configuration.
            - key (str): The key to be set.
            - value (Any): The value to be associated with the key.
            - to_site (bool, optional): Whether to set in site config. Default is False.
        """
        try:
            config_target = self.configSite if to_site else self.config
            
            if section not in config_target:
                config_target[section] = {}

            config_target[section][key] = value
            cache_key = f"{'site' if to_site else 'config'}.{section}.{key}"
            self.cache[cache_key] = value

        except Exception as e:
            print(f"Error setting key '{key}' in section '{section}' of {'site' if to_site else 'main'} config: {e}")

    def write_config(self) -> None:
        """Write the main configuration to the file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error writing configuration file: {e}")


# Initialize
config_manager = ConfigManager()
config_manager.read_config()
