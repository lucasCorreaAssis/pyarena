from paho.mqtt import client as mqtt_client
from Multicore import Thread
from .Models.credentials import Credentials
from .Models.mqtt_config import MqttConfig
import uuid

class MqttClient(Thread):
    _config: MqttConfig
    _client: mqtt_client.Client
    _client_id: str

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def __init__(self, config: MqttConfig) -> None:
        super().__init__()
        self._config = config
        self._client_id = str(uuid.uuid4())

    def connect(self, credentials: Credentials = Credentials('', '')):
        self._client = mqtt_client.Client(self._client_id)
        self._client.username_pw_set(credentials.username, credentials.password)
        self._client.on_connect = self.on_connect
        self._client.connect(self._config.broker, self._config.port)

    def run(self):
        self._client.loop_start()
        while self.thread_running():
            pass
        self._client.loop_stop()
