# 🖥️ Wake-on-LAN MQTT Controller

Ce projet permet de contrôler l’allumage d’un PC Windows via MQTT en utilisant le protocole **Wake-on-LAN**.  
Le script tourne dans un conteneur Docker, écoute les topics MQTT définis, et vérifie l’état de la machine toutes les 5 minutes. Il y a une protection contre le spam de la fonctionnalité du WOL qui ne peux se declancher toutes les 5 minutes.
Les logs sont print dans la sortie standard + dans le dossier logs + envoyé sur le topic debug en mqtt

---

## 🚀 Fonctionnalités

- 🔌 Wake-on-LAN automatique si la machine est demandée et hors-ligne
- 📡 Vérifie l’état du PC à l’aide de `ping` et `nslookup`
- 📤 Publie l’état (`on` / `off`) sur un topic MQTT
- 🔒 Anti-spam : cooldown configurable entre deux envois WOL
- 🐳 100% compatible avec Home Assistant via MQTT
- 📄 Logs enrichis (niveau configurable via variable d’environnement)

---


---

## 🧾 Exemple de `mqtt.ini`

```ini
[MQTT]
BROKER = 							; Adresse ip du Broker mqtt
PORT_WEBSOCKET =					; Port websocket du broker
USERNAME = 							; Username broker
PASSWORD =							; Password broker

[TOPIC]
WINDOB =							; Topic pour recevoir les commandes
WINDOB_GET =						; topic pour publier l’état
DEBUG =								; Topic pour les logs/debugs

[CIBLE]
IP =	 							; Ip destination
HOST =								; Hostaname destination

[MAC]
MAC_WIN =							; Adresse MAC pour le Wake-on-LAN
```
---

## 📁 Arborescence du projet

```sh 
check-hostname/
├── app/ 	
│ 			├── conf/ 
│ 			│ └── mqtt.ini 
│ 			├── script/ 
│ 			│ ├── check-hostname.py
│ 			│ ├── logger.py 
│ 			│ └── __init__.py
|			├── logs/
│ 			├── Dockerfile 
│ 			└── requirements.txt 
└── docker-compose.yml
```
