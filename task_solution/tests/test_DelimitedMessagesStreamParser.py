from parser.parserTools import DelimitedMessagesStreamParser
from proto.message_pb2 import WrapperMessage

from google.protobuf.internal.encoder import _VarintBytes

import unittest


class DelimitedMessagesStreamParserTest(unittest.TestCase):

    def test_all_good(self):
        msg1, msg2, msg3, msg4 = WrapperMessage(), WrapperMessage(), WrapperMessage(), WrapperMessage()
        msg1.fast_response.current_date_time = "10"
        msg2.slow_response.connected_client_count = 10
        msg3.request_for_fast_response.SetInParent()
        msg4.request_for_slow_response.time_in_seconds_to_sleep = 10

        messages = _VarintBytes(msg1.ByteSize()) + msg1.SerializeToString()
        messages += _VarintBytes(msg2.ByteSize()) + msg2.SerializeToString()
        messages += _VarintBytes(msg3.ByteSize()) + msg3.SerializeToString()
        messages += _VarintBytes(msg4.ByteSize()) + msg4.SerializeToString()

        parser = DelimitedMessagesStreamParser(WrapperMessage)
        list_msg: list[WrapperMessage] = []

        for byte in messages:
            parsed_messages = parser.parse(byte.to_bytes(1, "little"))
            for value in parsed_messages:
                list_msg.append(value)

        self.assertEqual(len(list_msg), 4)

        it = iter(list_msg)

        self.assertTrue(next(it).HasField("fast_response"))
        self.assertTrue(next(it).HasField("slow_response"))
        self.assertTrue(next(it).HasField("request_for_fast_response"))
        self.assertTrue(next(it).HasField("request_for_slow_response"))

        try:
            next(it)
            self.assertTrue(False)
        except StopIteration:
            self.assertTrue(True)

    def test_empty_data(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        self.assertEqual(parser.parse(b''), [])
        self.assertEqual(parser.parse(''), [])

    def test_wrong_size(self):
        msg = WrapperMessage()
        msg.fast_response.current_date_time = "10"
        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()

        parser = DelimitedMessagesStreamParser(WrapperMessage)

        self.assertEqual(parser.parse(data[:-1]), [])
        self.assertEqual(len(parser.parse(data + b'\x02')), 1)

    def test_any_data(self):
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        self.assertEqual(parser.parse(b'daxsdasdas'), [])
        self.assertEqual(parser.parse(b'1231231231'), [])
        self.assertEqual(parser.parse('daxsdasdasa'), [])
        self.assertEqual(parser.parse('12312312312'), [])

    def test_corrupted_data(self):
        msg = WrapperMessage()
        msg.fast_response.current_date_time = "10"
        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()
        parser = DelimitedMessagesStreamParser(WrapperMessage)

        data = data[:3] + b'k' + data[4:]
        self.assertEqual(parser.parse(data), [])
        data = data[:4] + b'e' + data[5:]
        self.assertEqual(parser.parse(data), [])
        data = data[:5] + b'k' + data[6:]
        self.assertEqual(parser.parse(data), [])

        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()
        data = data[0:1]
        self.assertEqual(parser.parse(data), [])
