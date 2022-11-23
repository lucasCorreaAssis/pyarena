from .mqtt_client import MqttClient

class MqttSubscriber(MqttClient):

    @staticmethod
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def subscribe(self):
        self._client.subscribe(self._config.topic)
        self._client.on_message = self.on_message

    def loop(self):
        self._client.loop_forever()
