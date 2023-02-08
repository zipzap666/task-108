from src.proto.message_pb2 import WrapperMessage
from src.parser.parserTools import parse_delimited as parseDelimited
from google.protobuf.internal.encoder import _VarintBytes
import unittest


class ParseDelimitedTest(unittest.TestCase):
    def test_all_good(self):
        msg1, msg2, msg3, msg4 = WrapperMessage(
        ), WrapperMessage(), WrapperMessage(), WrapperMessage()
        msg1.fast_response.current_date_time = "10"
        msg2.slow_response.connected_client_count = 10
        msg3.request_for_fast_response.SetInParent()
        msg4.request_for_slow_response.time_in_seconds_to_sleep = 10

        data = _VarintBytes(msg1.ByteSize()) + msg1.SerializeToString()
        test, bytes_consumed = parseDelimited(data, WrapperMessage)

        self.assertEqual(test.HasField("fast_response"), True)
        self.assertEqual(test.HasField("slow_response"), False)
        self.assertEqual(test.HasField("request_for_fast_response"), False)
        self.assertEqual(test.HasField("request_for_slow_response"), False)
        self.assertEqual(bytes_consumed, len(data))
        self.assertEqual(test.fast_response.current_date_time, "10")

        data = _VarintBytes(msg2.ByteSize()) + msg2.SerializeToString()
        test, bytes_consumed = parseDelimited(data, WrapperMessage)

        self.assertEqual(test.HasField("fast_response"), False)
        self.assertEqual(test.HasField("slow_response"), True)
        self.assertEqual(test.HasField("request_for_fast_response"), False)
        self.assertEqual(test.HasField("request_for_slow_response"), False)
        self.assertEqual(bytes_consumed, len(data))
        self.assertEqual(test.slow_response.connected_client_count, 10)

        data = _VarintBytes(msg3.ByteSize()) + msg3.SerializeToString()
        test, bytes_consumed = parseDelimited(data, WrapperMessage)

        self.assertEqual(test.HasField("fast_response"), False)
        self.assertEqual(test.HasField("slow_response"), False)
        self.assertEqual(test.HasField("request_for_fast_response"), True)
        self.assertEqual(test.HasField("request_for_slow_response"), False)
        self.assertEqual(bytes_consumed, len(data))

        data = _VarintBytes(msg4.ByteSize()) + msg4.SerializeToString()
        test, bytes_consumed = parseDelimited(data, WrapperMessage)

        self.assertEqual(test.HasField("fast_response"), False)
        self.assertEqual(test.HasField("slow_response"), False)
        self.assertEqual(test.HasField("request_for_fast_response"), False)
        self.assertEqual(test.HasField("request_for_slow_response"), True)
        self.assertEqual(bytes_consumed, len(data))
        self.assertEqual(
            test.request_for_slow_response.time_in_seconds_to_sleep, 10)

    def test_empty_data(self):
        self.assertIsNone(parseDelimited(b'', WrapperMessage)[0])
        self.assertIsNone(parseDelimited("", WrapperMessage)[0])
        self.assertIsNone(parseDelimited(None, WrapperMessage)[0])

    def test_wrong_size(self):
        msg = WrapperMessage()
        msg.fast_response.current_date_time = "10"
        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()

        self.assertIsNone(parseDelimited(data[:-1], WrapperMessage)[0])
        self.assertIsNotNone(parseDelimited(data + b'\x02', WrapperMessage)[0])

    def test_any_data(self):
        self.assertIsNone(parseDelimited(
            b'125421587125912', WrapperMessage)[0])
        self.assertIsNone(parseDelimited(
            b'sadfasdfasdfads', WrapperMessage)[0])

    def test_corrupted_data(self):
        msg = WrapperMessage()
        msg.fast_response.current_date_time = "10"
        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()

        data = data[:3] + b'k' + data[4:]
        self.assertIsNone(parseDelimited(data, WrapperMessage)[0])
        data = data[:4] + b'e' + data[5:]
        self.assertIsNone(parseDelimited(data, WrapperMessage)[0])
        data = data[:5] + b'k' + data[6:]
        self.assertIsNone(parseDelimited(data, WrapperMessage)[0])

        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()
        data = data[0:1]
        self.assertIsNone(parseDelimited(data, WrapperMessage)[0])

    def test_bytes_consumed(self):
        msg = WrapperMessage()
        msg.fast_response.current_date_time = "10"
        data = _VarintBytes(msg.ByteSize()) + msg.SerializeToString()

        self.assertEqual(parseDelimited(data, WrapperMessage)[1], len(data))
        self.assertEqual(parseDelimited(data[:-2], WrapperMessage)[1], 0)
        self.assertEqual(parseDelimited(
            data + b'123', WrapperMessage)[1], len(data))
