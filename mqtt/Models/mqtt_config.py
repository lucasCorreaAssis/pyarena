from dataclasses import dataclass

@dataclass
class MqttConfig:
    topic: str
    broker: str
    port: int