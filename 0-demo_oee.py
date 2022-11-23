from oee_subscriber import OeeSubscriber
from mqtt import MqttConfig
import time

config = MqttConfig('test', 'localhost', 1883)
oee = OeeSubscriber(config)
oee.start()
time.sleep(20)
oee.stop()
