from decision_subscriber import DecisionSubscriber
from mqtt import MqttConfig
import time

config = MqttConfig('test', 'localhost', 1883)
operations = ['OP1', 'OP2']
decision = DecisionSubscriber(config, operations)
decision.start()

# Only for demo purpose
time.sleep(3)

try:
    while True:
        decision.prioritize()
        time.sleep(3)
except KeyboardInterrupt:
    print('Stopping decision!')
    decision.stop()
