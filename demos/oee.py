from oee_subscriber import OeeSubscriber
from mqtt import MqttConfig

config = MqttConfig('test', 'localhost', 1883)
oee = OeeSubscriber(config)
oee.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping OEE!')
    oee.stop()

