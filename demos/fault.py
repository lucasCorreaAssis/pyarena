from fault_subscriber import faultsubscriber
from mqtt import MqttConfig

config = MqttConfig('test', 'localhost', 1883)
fault = faultsubscriber(config)
fault.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping Fault!')
    fault.stop()