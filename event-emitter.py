
from abc import ABC, abstractclassmethod
import pandas as pd

class EventEmitter(ABC):
    @abstractclassmethod
    def loadHistoricData():
        pass

    @abstractclassmethod
    def emitNext(timestamp):
        pass

class MQTTEventEmitter(EventEmitter):
    def __init__(self) -> None:
        super().__init__()
        self.dataframe = pd.DataFrame()
        self.current_index = 0

    def loadHistoricData(self, csv_path: str):
        self.dataframe = pd.read_csv(csv_path)

    def emitNext(self, timestamp):
        self.dataframe.iloc[self.current_index]
        
        self.current_index += 1

        # add code of publisher!!!
