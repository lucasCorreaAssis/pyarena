from event_emitter import MQTTEventEmitter
from mqtt import MqttConfig

config = MqttConfig('parts', 'localhost', 1883)

emitter = MQTTEventEmitter(config)
emitter.loadHistoricData('samples/good-parts.csv')
emitter.emitNext()
