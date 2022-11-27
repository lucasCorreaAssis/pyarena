from dataclasses import dataclass
import json
from typing import List
from decision import ProductionOrderPriorization
from mqtt import MqttSubscriber, MqttConfig
from paho.mqtt.client import MQTTMessage
from promethee import Promethee
import numpy as np
import threading

@dataclass
class OperationValue:
    operation: str
    value: float

class DecisionSubscriber:
    _config: MqttConfig
    _threads: List[MqttSubscriber]
    _operations: List[str]
    _last_quality: List[OperationValue] = []
    _last_availability: List[OperationValue] = []
    _last_production: List[OperationValue] = []
    _last_mtbf: List[OperationValue] = []
    _last_mttr: List[OperationValue] = []
    _decision_model: Promethee
    _lock: threading.Lock

    def __init__(self, config: MqttConfig, operations: List[str]):
        self._config = config
        self._threads = []
        self._operations = operations
        self._decision_model = ProductionOrderPriorization(operations)
        self._lock = threading.Lock()
        for operation in operations:
            self._last_quality.append(OperationValue(operation, 0.0))
            self._last_availability.append(OperationValue(operation, 0.0))
            self._last_production.append(OperationValue(operation, 0.0))
            self._last_mtbf.append(OperationValue(operation, 0.0))
            self._last_mttr.append(OperationValue(operation, 0.0))

    def start(self):
        self._threads.append(self._create_subscriber_for_topic('quality', self._on_quality))
        self._threads.append(self._create_subscriber_for_topic('availability', self._on_availability))
        self._threads.append(self._create_subscriber_for_topic('production', self._on_production))
        self._threads.append(self._create_subscriber_for_topic('mtbf', self._on_mtbf))
        self._threads.append(self._create_subscriber_for_topic('mttr', self._on_mttr))

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

    def _on_quality(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        for i, operation in enumerate(self._operations):
            if operation == payload['operation']:
                self._last_quality[i].value = payload['value']

        self._prioritize()

    def _on_availability(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        for i, operation in enumerate(self._operations):
            if operation == payload['operation']:
                self._last_availability[i].value = payload['value']
        
        self._prioritize()

    def _on_production(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        for i, operation in enumerate(self._operations):
            if operation == payload['operation']:
                self._last_production[i].value = payload['value']

        self._prioritize()

    def _on_mtbf(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        for i, operation in enumerate(self._operations):
            if operation == payload['operation']:
                self._last_mtbf[i].value = payload['value']

        self._prioritize()

    def _on_mttr(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        for i, operation in enumerate(self._operations):
            if operation == payload['operation']:
                self._last_mttr[i].value = payload['value']

        self._prioritize()

    def _prioritize(self):
        self._lock.acquire()
        quality = []
        availability = []
        production = []
        mttr = []
        mtbf = []
        for i,_ in enumerate(self._operations):
            quality.append(self._last_quality[i].value)
            availability.append(self._last_availability[i].value)
            production.append(self._last_production[i].value)
            mttr.append(self._last_mttr[i].value)
            mtbf.append(self._last_mtbf[i].value)

        values = np.array([
            quality,
            production,
            availability,
            mttr,
            mtbf
        ])

        output = self._decision_model.prioritize(values)
        for i, unicriteria_phi in enumerate(output.unicriteria_phi):
            print(f'{i}- {unicriteria_phi}\n')
        self._lock.release()
