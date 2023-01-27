from google.protobuf.internal import decoder
from copy import *
from proto.message_pb2 import *


def parse_delimited(data, typename):
    if data is None or len(data) == 0:
        return None

    length, pos = decoder._DecodeVarint32(data, 0)

    if length + pos > len(data):
        return None, 0

    message = typename
    message.ParseFromString(data[pos:pos+length])

    return message, length + pos


class DelimitedMessagesStreamParser:
    def __init__(self, type_msg) -> None:
        self.buffer = b''
        self.type_msg = type_msg

    def parse(self, data,):
        self.buffer += data
        byte_consumed = 0
        messages = []

        while True:
            prev = byte_consumed
            message, byte_consumed = parse_delimited(self.buffer[byte_consumed:], copy(self.type_msg))
            print(byte_consumed)

            if message is not None:
                messages.append(message)
            elif byte_consumed == prev:
                break

            if byte_consumed == len(self.buffer):
                break

        self.buffer = self.buffer[byte_consumed:]

        return messages


if __name__ == '__main__':
    # message = WrapperMessage()
    parser = DelimitedMessagesStreamParser(WrapperMessage())
    lst = parser.parse(b"\x05\n\x03\n\x01\x01\x05\n\x03\n\x01\x01")
