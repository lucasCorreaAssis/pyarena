from typing import List
from mqtt import MqttSubscriber, MqttConfig
from paho.mqtt.client import MQTTMessage

class LoggerSubscriber:
    _config: MqttConfig
    _threads: List[MqttSubscriber]

    def __init__(self, config: MqttConfig):
        self._config = config
        self._threads = []

    def start(self):
        self._threads.append(self._create_subscriber_for_topic('good_parts'))
        self._threads.append(self._create_subscriber_for_topic('bad_parts'))
        self._threads.append(self._create_subscriber_for_topic('fault'))
        self._threads.append(self._create_subscriber_for_topic('mtbf'))
        self._threads.append(self._create_subscriber_for_topic('mttr'))
        self._threads.append(self._create_subscriber_for_topic('quality'))
        self._threads.append(self._create_subscriber_for_topic('production'))
        self._threads.append(self._create_subscriber_for_topic('availability'))
        self._threads.append(self._create_subscriber_for_topic('oee'))

    def _create_subscriber_for_topic(self, topic) -> MqttSubscriber:
        config = MqttConfig(topic, self._config.broker, self._config.port)
        subscriber = MqttSubscriber(config)
        subscriber.connect()
        subscriber.subscribe(self._on_message)
        subscriber.start()
        return subscriber

    def stop(self):
        for thread in self._threads:
            thread.stop()
            thread.join()

    def _on_message(self, client, userdata, msg: MQTTMessage):
        print(f'received message {msg.payload} from {msg.topic}')