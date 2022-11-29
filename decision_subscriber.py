from dataclasses import dataclass
import json
from typing import List
from decision import ProductionOrderPriorization
from mqtt import MqttSubscriber, MqttConfig
from paho.mqtt.client import MQTTMessage
from promethee import Promethee
import numpy as np
import threading
import time

class DecisionSubscriber:
    _config: MqttConfig
    _threads: List[MqttSubscriber]
    _operations: List[str]
    _last_quality: dict[str, float] = {}
    _last_availability: dict[str, float] = {}
    _last_production: dict[str, float] = {}
    _last_mtbf: dict[str, float] = {}
    _last_mttr: dict[str, float] = {}
    _decision_model: Promethee
    _lock: threading.Lock

    def __init__(self, config: MqttConfig, operations: List[str]):
        self._config = config
        self._threads = []
        self._operations = operations
        self._decision_model = ProductionOrderPriorization(operations)
        self._lock = threading.Lock()
        for operation in operations:
            self._last_quality[operation] = 0.0
            self._last_availability[operation] = 0.0
            self._last_production[operation] = 0.0
            self._last_mtbf[operation] = 0.0
            self._last_mttr[operation] = 0.0

    def start(self):
        self.__running = True
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
        self._last_quality[payload['operation']] = payload['value']

    def _on_availability(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        self._last_availability[payload['operation']] = payload['value']
        
    def _on_production(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        self._last_production[payload['operation']] = payload['value']

    def _on_mtbf(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        self._last_mtbf[payload['operation']] = payload['value']

    def _on_mttr(self, client, userdata, msg: MQTTMessage):
        payload = json.loads(msg.payload)
        if not payload['operation'] in self._operations:
            return
        self._last_mttr[payload['operation']] = payload['value']

    def prioritize(self):
        self._lock.acquire()
        quality = []
        availability = []
        production = []
        mttr = []
        mtbf = []
        for operation in self._operations:
            quality.append(self._last_quality[operation])
            availability.append(self._last_availability[operation])
            production.append(self._last_production[operation])
            mttr.append(self._last_mttr[operation])
            mtbf.append(self._last_mtbf[operation])

        values = np.array([
            quality,
            production,
            availability,
            mttr,
            mtbf
        ])

        output = self._decision_model.prioritize(values)
        print('New priorization:')
        for i, unicriteria_phi in enumerate(output.unicriteria_phi):
            print(f'{i}- {unicriteria_phi}\n')
        self._lock.release()
