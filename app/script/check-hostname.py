import socket
import subprocess
import threading
from datetime import datetime, timedelta
from paho.mqtt import client as mqtt_client
import configparser
import os
import sys
from typing import Optional
from script.logger import logger
from script.config_validator import validate_config
from dotenv import load_dotenv
from wakeonlan import send_magic_packet

load_dotenv()

class MQTTConfig:
	def __init__(self, config_path: str):
		config = configparser.ConfigParser()
		config.read(config_path)

		self.broker = config['MQTT']['BROKER']
		self.port_ws = int(config['MQTT']['PORT_WEBSOCKET'])
		# self.port = int(config['MQTT']['PORT'])

		# self.topic_linux = config['TOPIC']['LINUX']
		# self.topic_linux_get = config['TOPIC']['LINUX_GET']
		self.topic_windows = config['TOPIC']['WINDOB']
		self.topic_windows_get = config['TOPIC']['WINDOB_GET']
		self.topic_debug = config['TOPIC'].get('DEBUG', '')
		self.debug_enabled = os.getenv('DISABLE_MQTT_DEBUG', 'false').lower() != 'true'

		# self.ip_linux = config['CIBLE']['IP_LINUX']
		self.ip_windows = config['CIBLE']['IP']
		# self.host_linux = config['CIBLE']['HOST_LINUX']
		self.host_windows = config['CIBLE']['HOST']

		self.mac_win = config['MAC']['MAC_WIN']

class HostChecker:
	def __init__(self, config: MQTTConfig, interval: int = 300):
		self.config = config
		self.interval = interval
		self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id='01', transport='websockets')
		# self.last_execution_time = datetime.now() - timedelta(minutes=5)
		self.last_wol_sent = datetime.now() - timedelta(minutes=5) # Protection anti spam timer
		self.wol_cooldown = timedelta(minutes=3)

	def start(self):
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(self.config.broker, self.config.port_ws, 60)
		self.client.loop_start()
		threading.Timer(self.interval, self.periodic_check).start()

	def publish_debug(self, msg: str, topic: Optional[str] = None) -> None:
		topic = topic or self.config.topic_debug
		info = "File check-hostname -- "
		end_info = " -- "
		logger.info(msg + end_info)
		if not self.config.debug_enabled:
			return
		self.publish_status(topic, info + msg + end_info)

	def is_host_up(self, ip: str) -> bool:
		try:
			subprocess.check_output(["ping", "-c", "1", ip])
			return True
		except subprocess.CalledProcessError as e:
			self.publish_debug(f"Failed to ping {ip}: {e.output}")
			return False

	def get_hostname(self, ip: str) -> str:
		try:
			result = subprocess.check_output(["nslookup", ip, "192.168.1.1"]).decode('utf-8')
			for line in result.splitlines():
				if "name =" in line:
					hostname = line.split('=')[-1].strip().rstrip('.')
					for suffix in ['.home', '-1']:
						if hostname.endswith(suffix):
							hostname = hostname[:-len(suffix)]
					return hostname
		except Exception as e:
			self.publish_debug(f"Error resolving {ip}: {e}")
		return "Unknown"

	def publish_status(self, topic: str, message: str) -> None:
		self.client.publish(topic, message, qos=1)

	def wake_on_lan(self, mac: str) -> None:
		self.publish_debug(f"Sending Wake-on-LAN packet to {mac}")
		try:
			send_magic_packet(mac)
			self.publish_debug("WOL packet sent successfully.")
		except Exception as e:
			self.publish_debug(f"Error sending WOL packet: {e}")

	def update_status(self) -> None:
		if self.is_host_up(self.config.ip_windows):
			hostname = self.get_hostname(self.config.ip_windows)
			self.publish_debug(f"ONLINE: {hostname}")
			# if hostname == self.config.host_linux:
				# self.publish_status(self.config.topic_linux_get, "on")
				# self.publish_status(self.config.topic_windows_get, "off")
				# return
			if hostname == self.config.host_windows:
				# self.publish_status(self.config.topic_linux_get, "off")
				self.publish_status(self.config.topic_windows_get, "on")
				return

		self.publish_debug("OFFLINE")
		# self.publish_status(self.config.topic_linux_get, "off")
		self.publish_status(self.config.topic_windows_get, "off")

	def handle_direct_command(self, topic: str, message: str) -> None:
		self.publish_debug(f"Handling direct command for {topic} with message {message}")

		if topic == self.config.topic_windows and message == "on":
			if not self.is_host_up(self.config.ip_windows):
				now = datetime.now()
				if now - self.last_wol_sent >= self.wol_cooldown:
					self.publish_debug("Windows is offline, sending WOL...")
					self.wake_on_lan(self.config.mac_win)
					self.last_wol_sent = now
				else:
					remaining = self.wol_cooldown - (now - self.last_wol_sent)
					self.publish_debug(f"WOL skipped: cooldown active ({remaining.seconds}s left)")
			else:
				self.publish_debug("Windows is already online, skipping WOL.")
		else:
			self.update_status()

	def periodic_check(self) -> None:
		self.update_status()
		next_check = datetime.now() + timedelta(seconds=self.interval)
		self.publish_debug(f"Next status update scheduled at {next_check.strftime('%H:%M:%S')}")
		threading.Timer(self.interval, self.periodic_check).start()

	def on_connect(self, client, userdata, flags, rc, other) -> None:
		if rc == 0:
			self.publish_debug("Connected to MQTT Broker!")
			client.subscribe(self.config.topic_debug, qos=1)
			# client.subscribe(self.config.topic_linux, qos=1)
			# client.subscribe(self.config.topic_linux_get, qos=1)
			client.subscribe(self.config.topic_windows, qos=1)
			client.subscribe(self.config.topic_windows_get, qos=1)
		else:
			self.publish_debug(f"Failed to connect, return code {rc}")

	def on_message(self, client, userdata, msg) -> None:
		logger.debug(f"CLIENT: {client._client_id.decode()} | TOPIC: {msg.topic} | MSG: {msg.payload.decode()}")
		if msg.topic == self.config.topic_windows:
			if msg.payload.decode() != 'off':
				self.handle_direct_command(msg.topic, msg.payload.decode())



def main():
	config_path = os.path.join(os.path.dirname(__file__), '..', 'conf', 'mqtt.ini')
	config = validate_config(config_path)
	config = MQTTConfig(config_path)
	checker = HostChecker(config)
	checker.start()

if __name__ == "__main__":
	main()
