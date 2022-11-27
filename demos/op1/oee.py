from oee_subscriber import OeeSubscriber
from mqtt import MqttConfig

bi = f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/00efeb83-e802-4be0-a091-85347beddc60/rows?key=Fa2TgypYwwtqLESfXaXe1op7d9sSATOOBPMBoQbar%2BJ2Xhr%2BxGcPG3O4Tuei%2FnZqMrnH9CUgou6p4il8E7PoWA%3D%3D'
config = MqttConfig('test', 'localhost', 1883)
oee = OeeSubscriber(config, 'OP1', bi)
oee.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping OEE!')
    oee.stop()

