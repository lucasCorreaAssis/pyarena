
from abc import ABC, abstractclassmethod

class HistoricEventEmitter(ABC):
    @abstractclassmethod
    def loadHistoricData():
        pass

    @abstractclassmethod
    def emitNext():
        pass

class GoodPartsEmitter(HistoricEventEmitter):
    pass

class BadPartsEmitter(HistoricEventEmitter):
    pass

# How to load file, constructor? method?

# Do we need an orchestrator to handle when to emit next?

# Or should the emit next method receive a reference timestamp?
