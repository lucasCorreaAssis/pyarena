
from .mqtt_client import MqttClient


class MqttPublisher(MqttClient):
    def publish(self, message, topic):
        result = self._client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Send `{message}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def loop(self):
        self._client.loop_start()