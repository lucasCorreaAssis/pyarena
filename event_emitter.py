from abc import ABC, abstractclassmethod
import time
import pandas as pd
from mqtt import MqttPublisher, MqttConfig

class EventEmitter(ABC):
    @abstractclassmethod
    def loadHistoricData():
        pass

    @abstractclassmethod
    def start(timestamp):
        pass

class MQTTEventEmitter(EventEmitter):
    _config: MqttConfig
    _dataframe: pd.DataFrame
    _current_index: int
    _publisher: MqttPublisher
    _last_timestamp: float

    def __init__(self, config: MqttConfig) -> None:
        super().__init__()
        self._config = config
        self._current_index = 0
        self._last_timestamp = 0
        self._publisher = MqttPublisher(config)
        self._publisher.connect()

    def loadHistoricData(self, csv_path: str):
        self.dataframe = pd.read_csv(csv_path, delimiter=';')

    def start(self):
        while len(self.dataframe) > self._current_index + 1:
            current_timestamp = self.dataframe.iloc[self._current_index]['timestamp']
            self._emitNext()
            self._current_index += 1
            next_timestamp = self.dataframe.iloc[self._current_index]['timestamp']
            time_to_next_event = float(next_timestamp) - float(current_timestamp)
            print(f'waiting for {time_to_next_event} s')
            time.sleep(time_to_next_event)

    def _emitNext(self):
        row = self.dataframe.iloc[self._current_index]
        if row['good_parts'] > 0:
            self._publisher.publish(str(row['good_parts']), 'good_parts')
        if row['bad_parts'] > 0:
            self._publisher.publish(str(row['bad_parts']), 'bad_parts')
        if row['fault'] > 0:
            self._publisher.publish(str(row['fault']), 'fault')
