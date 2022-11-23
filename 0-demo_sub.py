from mqtt import MqttConfig, MqttSubscriber

config = MqttConfig('test', 'localhost', 1883)

sub = MqttSubscriber(config)

sub.connect()
sub.subscribe()
sub.loop()
