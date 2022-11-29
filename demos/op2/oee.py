from oee_subscriber import OeeSubscriber
from mqtt import MqttConfig

bi = f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/f065ddbd-5219-4243-bcc4-998b5793df8a/rows?key=QblqkGPzOI3xKdVhvJMbVXP6aqtX062QwX1meLCoHyAXWoFr3GgaHkTMEcUv0UwLEGwfsJ%2FD0X6dz56Kfn3QFg%3D%3D'
config = MqttConfig('test', 'localhost', 1883)
oee = OeeSubscriber(config, 'OP2', bi, 0.8)
oee.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping OEE!')
    oee.stop()

