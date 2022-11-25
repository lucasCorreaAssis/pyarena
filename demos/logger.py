from logger_subscriber import LoggerSubscriber
from mqtt import MqttConfig
import time

config = MqttConfig('test', 'localhost', 1883)
logger = LoggerSubscriber(config)
logger.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping logger!')
    logger.stop()
