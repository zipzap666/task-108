from typing import TypeVar, Type
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.message import DecodeError


def parse_delimited(data, message_type):
    if data is None or len(data) == 0:
        return None, 0

    try:
        length, pos = _DecodeVarint32(data, 0)
    except TypeError:
        return None, 0

    if length + pos > len(data):
        return None, 0

    message = message_type()
    try:
        message.ParseFromString(data[pos:pos + length])
    except DecodeError:
        return None, pos + length

    return message, pos + length


T = TypeVar('T')


class DelimitedMessagesStreamParser:
    def __init__(self, type_msg: Type[T]):
        self.type_msg = type_msg
        self.buffer: bytearray = b''

    def parse(self, data) -> list[Type[T]]:
        try:
            self.buffer += data
        except TypeError:
            return []

        messages: list[Type[T]] = []
        while len(self.buffer):
            message, bytes_consumed = parse_delimited(self.buffer, self.type_msg)
            if message:
                messages.append(message)
            elif bytes_consumed == 0:
                break

            self.buffer = self.buffer[bytes_consumed:]

        return messages
