import configparser
import os
from typing import List
from script.logger import logger

REQUIRED_SECTIONS = {
    "MQTT": ["BROKER", "PORT_WEBSOCKET", "USERNAME", "PASSWORD"],
    "TOPIC": ["WINDOB", "WINDOB_GET"],
    "CIBLE": ["IP", "HOST"],
    "MAC": ["MAC_WIN"]
}


def validate_config(config_path: str) -> configparser.ConfigParser:
	logger.info("Validating mqtt.ini configuration file...")

	if not os.path.exists(config_path):
		logger.critical(f"Configuration file not found at path: {config_path}")
		raise FileNotFoundError(f"Configuration file not found at {config_path}")

	config = configparser.ConfigParser()
	config.read(config_path)

	missing_sections: List[str] = []
	missing_keys: List[str] = []

	for section, keys in REQUIRED_SECTIONS.items():
		if section not in config:
			missing_sections.append(section)
		else:
			for key in keys:
				if key not in config[section]:
					missing_keys.append(f"{section}.{key}")

	if missing_sections or missing_keys:
		if missing_sections:
			logger.critical(f"Missing sections in config file: {missing_sections}")
		if missing_keys:
			logger.critical(f"Missing keys in config file: {missing_keys}")
		raise ValueError("Configuration file validation failed.")

	logger.info("✅ Configuration file is valid.")
	return config
