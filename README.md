## run:
    ./run_test

# Task:

## на основании постановки в LEARNING_CENTER-102 реализовать тоже самое на питоне
## для питона нужно будет использовать _DecodeVarint32 примерно так:
    (message_size, pos) = _DecodeVarint32(bytes_, start)
    current_message = bytes_[pos:(frame_size + pos)]
    
bytes_ - входные данные, полученные из сокета(например, прочитанные функцией readAll() или еще какой-то)

start - это указание на начало интересующего нас куска в bytes_(там лежат N сообщений, предваренных размером в Varint32)

для первого сообщения start равен 0

message_size - это размер сообщения

pos - это начало сообщения

current_message - это само сообщение
