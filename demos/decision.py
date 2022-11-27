from decision_subscriber import DecisionSubscriber
from mqtt import MqttConfig
import time

config = MqttConfig('test', 'localhost', 1883)
operations = ['OP1', 'OP2']
logger = DecisionSubscriber(config, operations)
logger.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping decision!')
    logger.stop()
