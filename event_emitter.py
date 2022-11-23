
from abc import ABC, abstractclassmethod
import pandas as pd
from mqtt import MqttPublisher, MqttConfig

class EventEmitter(ABC):
    @abstractclassmethod
    def loadHistoricData():
        pass

    @abstractclassmethod
    def emitNext(timestamp):
        pass

class MQTTEventEmitter(EventEmitter):
    _config: MqttConfig
    _dataframe: pd.DataFrame
    _current_index: int
    _publisher: MqttPublisher

    def __init__(self, config: MqttConfig) -> None:
        super().__init__()
        self._config = config
        self._current_index = 0
        self._publisher = MqttPublisher(config)
        self._publisher.connect()

    def loadHistoricData(self, csv_path: str):
        self.dataframe = pd.read_csv(csv_path, delimiter=';')

    # Review Timestamp
    def emitNext(self, timestamp = 100000):
        row = self.dataframe.iloc[self._current_index]
        if (row['timestamp'] > timestamp):
            return

        self._publisher.publish(str(row['good_part']), self._config.topic)
        self._current_index += 1
