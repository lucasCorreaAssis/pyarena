from typing import List
from mqtt import MqttSubscriber, MqttConfig, MqttPublisher
from paho.mqtt.client import MQTTMessage
import http.client
import json
import time

class OeeSubscriber:
    _initial_timestamp: float
    _bi: str
    _operation: str
    _config: MqttConfig
    _publisher: MqttPublisher
    _threads: List[MqttSubscriber]
    _total_parts: int
    _total_stop_time: float
    _total_good_parts: int
    _IDEAL_PRODUCTION: int
    _WORK_TIME: float


    def __init__(self, config: MqttConfig, operation: str, bi: str):
        self._initial_timestamp = time.time()
        self._bi = bi
        self._operation = operation
        self._config = config
        self._threads = []
        self._total_parts = 0
        self._total_stop_time = 0.0
        self._total_good_parts = 0
        self._publisher = MqttPublisher(config)
        self._publisher.connect()

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
        payload = json.loads(msg.payload)
        if payload['operation'] != self._operation:
            return
        self._total_good_parts += 1
        self._total_parts += 1
        self._update_oee()
 
    def _on_message_bad(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if payload['operation'] != self._operation:
            return
        self._total_parts += 1
        self._update_oee()

    def _on_message_fault(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if payload['operation'] != self._operation:
            return
        self._total_stop_time += float(payload['value'])
        self._update_oee()

    def _update_oee(self):
        work_time = time.time() - self._initial_timestamp
        ideal_production = work_time * 0.2
        quality = (self._total_good_parts / self._total_parts)*100
        availability = ((work_time - self._total_stop_time) / work_time)*100
        production = (self._total_parts / ideal_production)*100
        if production > 100:
            production = 100
        if quality > 100:
            quality = 100
        if availability > 100:
            availability = 100
        oee = production*quality*availability/100**2
        self._publish(quality, availability, production, oee)
        self._update_bi(quality, availability, production, oee)

    def _publish(self, quality, availability, production, oee):
        payload = {
            "operation": self._operation,
            "value": quality
        }
        self._publisher.publish(json.dumps(payload), 'quality')
        payload['value'] = availability
        self._publisher.publish(json.dumps(payload), 'availability')
        payload['value'] = production
        self._publisher.publish(json.dumps(payload), 'production')
        payload['value'] = oee
        self._publisher.publish(json.dumps(payload), 'oee')

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
        connection.request('POST', self._bi, json_body, headers)
        connection.getresponse()
