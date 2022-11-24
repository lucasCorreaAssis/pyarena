from typing import List
from mqtt import MqttSubscriber, MqttConfig
from paho.mqtt.client import MQTTMessage
import http.client
import json
import random

class OeeSubscriber:
    _config: MqttConfig
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
        self._IDEAL_PRODUCTION = 100 # TODO
        self._WORK_TIME = 1000 # TODO
        self._total_good_parts = 0       

    def start(self):
        good_parts_subscriber = self._subscribe_to_good_parts()
        bad_parts_subscriber = self._subscribe_to_bad_parts()
        fault_subscriber = self._subscribe_to_faults()
        self._threads.append(good_parts_subscriber, bad_parts_subscriber, fault_subscriber)

    def _subscribe_to_faults(self):
        fault_config = MqttConfig('fault', self._config.broker, self._config.port)
        fault_subscriber = MqttSubscriber(fault_config)
        fault_subscriber.connect()
        fault_subscriber.subscribe(self._on_message_parts)
        fault_subscriber.start()
        return fault_subscriber

    def _subscribe_to_bad_parts(self) -> MqttSubscriber:
        bad_config = MqttConfig('bad_parts', self._config.broker, self._config.port)
        bad_subscriber = MqttSubscriber(bad_config)
        bad_subscriber.connect()
        bad_subscriber.subscribe(self._on_message_parts)
        bad_subscriber.start()
        return bad_subscriber

    def _subscribe_to_good_parts(self) -> MqttSubscriber:
        good_config = MqttConfig('good_parts', self._config.broker, self._config.port)
        good_subscriber = MqttSubscriber(good_config)
        good_subscriber.connect()
        good_subscriber.subscribe(self._on_message_parts)
        good_subscriber.start()
        return good_subscriber

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
        quality = self._total_good_parts / self. self._total_parts
        availability = (self._WORK_TIME - self._total_stop_time) / self._WORK_TIME
        production = random.uniform(75, 85)

        connection = http.client.HTTPSConnection('api.powerbi.com')

        headers = {'Content-type': 'application/json'}

        body = [
            {
                "oee" : production*quality*availability/100**2,
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
