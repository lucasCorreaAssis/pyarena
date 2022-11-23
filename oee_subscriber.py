from typing import List
from mqtt import MqttSubscriber, MqttConfig
from paho.mqtt.client import MQTTMessage
import http.client
import json
import random

class OeeSubscriber:
    _config: MqttConfig
    _threads: List[MqttSubscriber]

    def __init__(self, config: MqttConfig):
        self._config = config
        self._threads = []

    def start(self):
        parts_subscriber = self._subscribe_to_parts()
        # Implement remaining subscribers
        # * Tempo parado
        self._threads.append(parts_subscriber)

    def _subscribe_to_parts(self) -> MqttSubscriber:
        parts_config = MqttConfig('parts', self._config.broker, self._config.port)
        parts_subscriber = MqttSubscriber(parts_config)
        parts_subscriber.connect()
        parts_subscriber.subscribe(self._on_message_parts)
        parts_subscriber.start()
        return parts_subscriber

    def stop(self):
        for thread in self._threads:
            thread.stop()
            thread.join()

    def _on_message_parts(self, client, userdata, msg: MQTTMessage):
        # NEED TO ESTIMATE KPIs

        qualidade = random.uniform(75, 85)
        disponibilidade = random.uniform(75, 85)
        producao = random.uniform(75, 85)

        self._update_oee(qualidade, disponibilidade, producao)

    def _update_oee(self, qualidade: float, disponibilidade: float, producao: float):
        connection = http.client.HTTPSConnection('api.powerbi.com')

        headers = {'Content-type': 'application/json'}

        body = [
            {
                "oee" : producao*qualidade*disponibilidade/100**2,
                "qualidade" :qualidade,
                "disponibilidade" :disponibilidade,
                "producao" :producao,
                "min": 0,
                "max": 100
            }
        ]
        json_body = json.dumps(body)

        connection.request('POST', f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/00efeb83-e802-4be0-a091-85347beddc60/rows?key=Fa2TgypYwwtqLESfXaXe1op7d9sSATOOBPMBoQbar%2BJ2Xhr%2BxGcPG3O4Tuei%2FnZqMrnH9CUgou6p4il8E7PoWA%3D%3D', json_body, headers)

        connection.getresponse()
