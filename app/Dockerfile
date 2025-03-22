FROM python:3.9-slim

# Installation des dépendances
RUN apt-get update && \
	apt-get install -y iputils-ping dnsutils && \
	rm -rf /var/lib/apt/lists/*

COPY ./ /app

RUN pip install --no-cache-dir -r /app/requirements.txt
# RUN pip install paho-mqtt paramiko

# RUN pip install --upgrade paho-mqtt

# Copie des scripts et fichiers de configuration dans l'image
# COPY ./script/ /app/script/
# COPY ./conf/ /app/conf/

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Commande pour exécuter le script Python
CMD ["python", "-m", "script.check-hostname"]
