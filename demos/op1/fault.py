from fault_subscriber import faultsubscriber
from mqtt import MqttConfig

bi = f'/beta/8a1ef6c3-8324-4103-bf4a-1328c5dc3653/datasets/30756df9-a74f-4058-811e-f933242aacb7/rows?key=pTOmZAoksa6hMT9sXvt11N79eyuX6sMY%2FLNlv25KdwBK0l%2B7D1x2ItpRSgGHx%2FO3MCmdFl1nKyAebV9rIBOFPw%3D%3D'
config = MqttConfig('test', 'localhost', 1883)
fault = faultsubscriber(config, 'OP1', bi)
fault.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping Fault!')
    fault.stop()