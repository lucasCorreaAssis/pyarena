from event_emitter import MQTTEventEmitter
from mqtt import MqttConfig

config = MqttConfig('parts', 'localhost', 1883)

emitter = MQTTEventEmitter(config, 'OP1')
emitter.loadHistoricData('samples/OP79505.csv')
emitter.start()

print('finished to emit all events!')