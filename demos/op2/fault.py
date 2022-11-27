from fault_subscriber import faultsubscriber
from mqtt import MqttConfig

bi = f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/3ea03396-98a0-43d4-bd73-6ab98cc02a2a/rows?key=mL%2FD%2FyQQVtdPQxtpNnBe2K73meJJG9WnZFhjYNuMIznMfH%2BFcPbmpiZgFIBBpY5klxtfJOGZqi7iqIUNB2cHzw%3D%3D'
config = MqttConfig('test', 'localhost', 1883)
fault = faultsubscriber(config, 'OP2', bi)
fault.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping Fault!')
    fault.stop()