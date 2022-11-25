from typing import List
from mqtt import MqttSubscriber, MqttConfig, MqttPublisher
from paho.mqtt.client import MQTTMessage
import http.client
import json
import time

class faultsubscriber:

    _config: MqttConfig
    _publisher: MqttPublisher
    _threads: List[MqttSubscriber]
    _mttr: float
    _mtbf: float
    _last_fault_timestamp: float

    def __init__(self, config: MqttConfig):
        self._config = config
        self._threads = []
        self._mttr = 0
        self._mtbf = 0
        self._last_fault_timestamp = 0
        self._publisher = MqttPublisher(config)
        self._publisher.connect()

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

        if self._last_fault_timestamp != 0:
            time_difference = time.time() - self._last_fault_timestamp
            self._mtbf = (self._mtbf + time_difference) / 2

        self._last_fault_timestamp = time.time()

        self._publish()
        self._update_bi()

    def _publish(self):
        self._publisher.publish(str(self._mttr), 'mttr')
        self._publisher.publish(str(self._mtbf), 'mtbf')

    def _update_bi(self):
        connection = http.client.HTTPSConnection('api.powerbi.com')
        headers = {'Content-type': 'application/json'}

        body = [
            {
                "mttr" : f'{self._mttr} s',
                "mtbf" : f'{self._mtbf} s'
            }
        ]
        json_body = json.dumps(body)

        connection.request('POST', f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/30756df9-a74f-4058-811e-f933242aacb7/rows?key=pTOmZAoksa6hMT9sXvt11N79eyuX6sMY%2FLNlv25KdwBK0l%2B7D1x2ItpRSgGHx%2FO3MCmdFl1nKyAebV9rIBOFPw%3D%3D', json_body, headers) 
        connection.getresponse()

    def stop(self):
        for thread in self._threads:
            thread.stop()
            thread.join()