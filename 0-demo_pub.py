
from mqtt import MqttConfig, MqttPublisher

config = MqttConfig('test', 'localhost', 1883)

pub = MqttPublisher(config)
pub.connect()
pub.loop()

pub.publish(topic='test', message='olá')