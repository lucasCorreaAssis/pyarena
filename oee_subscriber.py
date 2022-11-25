from typing import List
from mqtt import MqttSubscriber, MqttConfig, MqttPublisher
from paho.mqtt.client import MQTTMessage
import http.client
import json
import random

class OeeSubscriber:
    _config: MqttConfig
    _publisher: MqttPublisher
    _threads: List[MqttSubscriber]
    _total_parts: int
    _total_stop_time: float
    _total_good_parts: int
    _IDEAL_PRODUCTION: int
    _WORK_TIME: float


    def __init__(self, config: MqttConfig):
        self._config = config
        self._threads = []
        self._total_parts = 0
        self._total_stop_time = 0.0
        self._total_good_parts = 0
        self._publisher = MqttPublisher(config)
        self._publisher.connect()

        # MANUAL SETTINGS
        self._IDEAL_PRODUCTION = 10
        self._WORK_TIME = 9

    def start(self):
        self._threads.append(
            self._create_subscriber_for_topic('good_parts', self._on_message_good))
        self._threads.append(
            self._create_subscriber_for_topic('bad_parts', self._on_message_bad))
        self._threads.append(
            self._create_subscriber_for_topic('fault', self._on_message_fault))

    def _create_subscriber_for_topic(self, topic, callback) -> MqttSubscriber:
        config = MqttConfig(topic, self._config.broker, self._config.port)
        subscriber = MqttSubscriber(config)
        subscriber.connect()
        subscriber.subscribe(callback)
        subscriber.start()
        return subscriber

    def stop(self):
        for thread in self._threads:
            thread.stop()
            thread.join()

    def _on_message_good(self, client, userdata, msg: MQTTMessage):
        self._total_good_parts += 1
        self._total_parts += 1
        self._update_oee()
 
    def _on_message_bad(self, client, userdata, msg: MQTTMessage):
        self._total_parts += 1
        self._update_oee()

    def _on_message_fault(self, client, userdata, msg: MQTTMessage):
        self._total_stop_time += float(msg.payload)
        self._update_oee()

    def _update_oee(self):
        quality = (self._total_good_parts / self._total_parts)*100
        availability = ((self._WORK_TIME - self._total_stop_time) / self._WORK_TIME)*100
        production = (self._total_parts / self._IDEAL_PRODUCTION)*100
        oee = production*quality*availability/100**2

        self._publish(quality, availability, production, oee)
        self._update_bi(quality, availability, production, oee)

    def _publish(self, quality, availability, production, oee):
        self._publisher.publish(quality, 'quality')
        self._publisher.publish(availability, 'availability')
        self._publisher.publish(production, 'production')
        self._publisher.publish(oee, 'oee')

    def _update_bi(self, quality, availability, production, oee):
        connection = http.client.HTTPSConnection('api.powerbi.com')

        headers = {'Content-type': 'application/json'}

        body = [
            {
                "oee" : oee,
                "qualidade" :quality,
                "disponibilidade" :availability,
                "producao" :production,
                "min": 0,
                "max": 100
            }
        ]
        json_body = json.dumps(body)

        connection.request('POST', f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/00efeb83-e802-4be0-a091-85347beddc60/rows?key=Fa2TgypYwwtqLESfXaXe1op7d9sSATOOBPMBoQbar%2BJ2Xhr%2BxGcPG3O4Tuei%2FnZqMrnH9CUgou6p4il8E7PoWA%3D%3D', json_body, headers)
        connection.getresponse()
