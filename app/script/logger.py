import logging
import os
from logging.handlers import RotatingFileHandler
import emoji

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def get_log_level(level_str: str) -> int:
	return {
		"DEBUG": logging.DEBUG,
		"INFO": logging.INFO,
		"WARNING": logging.WARNING,
		"ERROR": logging.ERROR,
		"CRITICAL": logging.CRITICAL
	}.get(level_str, logging.INFO)


if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR, mode=0o777)

LOG_EMOJIS: dict[str, str] = {
	"DEBUG": "🔍",
	"INFO": "🪧",
	"WARNING": "⚠️",
	"ERROR": "❌",
	"CRITICAL": "🔥"
}

class EmojiFormatter(logging.Formatter):
	"""Ajoute un emoji correspondant au niveau du log sans erreur."""
	def format(self, record) -> str:
		if hasattr(record, "levelname") and record.levelname:
			if not any(emoji in record.levelname for emoji in LOG_EMOJIS.values()):
				emoji = LOG_EMOJIS.get(record.levelname, "📌")
				record.levelname = f"{emoji}  {record.levelname}"
		return super().format(record)

class EmojiLogger(logging.Logger):
	"""Logger qui ajoute automatiquement des emojis aux messages."""
	def __init__(self, name: str, log_file: str, level=logging.INFO, to_console: bool = True) -> None:
		super().__init__(name, level)

		if self.hasHandlers():
			return

		self.setLevel(level)
		self.propagate = False

		formatter = EmojiFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
		file_handler = RotatingFileHandler(os.path.join(LOG_DIR, log_file), maxBytes=1_000_000, backupCount=10)
		file_handler.setFormatter(formatter)
		file_handler.setLevel(level)
		self.addHandler(file_handler)

		if to_console:
			console_handler = logging.StreamHandler()
			console_handler.setFormatter(formatter)
			console_handler.setLevel(level)
			self.addHandler(console_handler)

	def emoji_log(self, level: int, message: str) -> None:
		"""Ajoute un emoji aux logs automatiquement."""
		message = emoji.emojize(message, language="alias")
		self.log(level, message)

	def debug(self, message: str, *args, **kwargs) -> None:
		super().debug(emoji.emojize(message, language="alias"), *args, **kwargs)

	def info(self, message: str, *args, **kwargs) -> None:
		super().info(emoji.emojize(message, language="alias"), *args, **kwargs)

	def warning(self, message: str, *args, **kwargs) -> None:
		super().warning(emoji.emojize(message, language="alias"), *args, **kwargs)

	def error(self, message: str, *args, **kwargs) -> None:
		super().error(emoji.emojize(message, language="alias"), *args, **kwargs)

	def critical(self, message: str, *args, **kwargs) -> None:
		super().critical(emoji.emojize(message, language="alias"), *args, **kwargs)


logger      = EmojiLogger("logger",     "logger.log",      get_log_level(LOG_LEVEL))
