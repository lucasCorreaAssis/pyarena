from typing import List
from mqtt import MqttSubscriber, MqttConfig
from paho.mqtt.client import MQTTMessage
import http.client
import json
import random

class faultsubscriber:

    _config: MqttConfig
    _threads: List[MqttSubscriber]
    _mttr: float
    _mtbf: float

    def __init__(self, config: MqttConfig):
        self._config = config
        self._threads = []
        self._mttr = 0
        self._mtbf = 0

    def start(self):
        fault_subscriber = self._subscribe_to_faults()
        self._threads.append(fault_subscriber)


    def _subscribe_to_faults(self):
        fault_config = MqttConfig('fault', self._config.broker, self._config.port)
        fault_subscriber = MqttSubscriber(fault_config)
        fault_subscriber.connect()
        fault_subscriber.subscribe(self._on_message_fault)
        fault_subscriber.start()
        return fault_subscriber

    def _on_message_fault(self, client, userdata, msg: MQTTMessage):
        fault = float(msg.payload)
        self._mttr = (self._mttr + fault) / 2
        # TODO MTBF
        # TODO UPDATE

    def _update_indica(self):
      
        connection = http.client.HTTPSConnection('api.powerbi.com')
        headers = {'Content-type': 'application/json'}

        body = [
            {
                "mttr" : self._mttr,
                "mtbf" : self._mtbf,
                
            }
        ]
        json_body = json.dumps(body)

        connection.request('POST', f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/00efeb83-e802-4be0-a091-85347beddc60/rows?key=Fa2TgypYwwtqLESfXaXe1op7d9sSATOOBPMBoQbar%2BJ2Xhr%2BxGcPG3O4Tuei%2FnZqMrnH9CUgou6p4il8E7PoWA%3D%3D', json_body, headers)

        connection.getresponse()

    def stop(self):
        for thread in self._threads:
            thread.stop()
            thread.join()