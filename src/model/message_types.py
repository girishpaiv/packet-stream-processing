from enum import Enum


class MessageType(Enum):
    """
    Configuring the Return values from Insights interface as Enums
    """
    PACKET = "packet"
    STREAM_RESOURCE_RESULT = "stream_resource_result"
    EXIT = "exit"
    CHILD_ENDED = "ended"
