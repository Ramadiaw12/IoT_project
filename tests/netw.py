import paho.mqtt.client as mqtt
import json
import time

# Configuration MQTT
BROKER = "localhost"   # ou "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/movement"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

def send_message(payload):
    client.publish(TOPIC, json.dumps(payload))
    # Vous pouvez mesurer la latence ici en enregistrant un timestamp