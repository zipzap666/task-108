protoc --python_out=. ./proto/message.proto
python3 -m unittest ./tests/test_DelimitedMessagesStreamParser.py
python3 -m unittest ./tests/test_parse_delimited.py