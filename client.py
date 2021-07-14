import socket
import attr
import threading


@attr.s(auto_attribs=True)
class Client:

    _server_ip_2con: str = attr.ib(default=None, init=True)
    _port_ip_2con: int = attr.ib(default=None, init=True)
    _tcp: bool = attr.ib(default=True, init=True)
    __client: socket.socket = attr.ib(default=None, init=False)
    __encoding_format: str = attr.ib(default="utf-8", init=True)
    __header_len: int = attr.ib(default=1024, init=True)

    def __attrs_post_init__(self):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((self._server_ip_2con, self._port_ip_2con))
        self.__username = input('Enter your username')
        username_len = str(len(self.__username))
        username_len = (username_len.encode(self.__encoding_format))
        username_len += b' ' * (self.__header_len - len(username_len))
        print(len(username_len))
        self.__client.send(username_len)
        self.__client.send(self.__username.encode(self.__encoding_format))
        print('Connected')

    def send_info(self, info):
        message = info.encode(self.__encoding_format)
        msg_len = len(message)
        send_len = str(msg_len).encode(self.__encoding_format)
        send_len += b' ' * (self.__header_len - len(send_len))
        self.__client.send(send_len)
        self.__client.send(message)

    def send_msg(self):
        while True:
            message = f'{self.__username}: {input("")}'
            self.send_info(message)

    def receive_msg(self):
        while True:
            message_len = self.__client.recv(self.__header_len).decode(self.__encoding_format)
            if message_len:
                msg_len = int(message_len)
                msg = self.__client.recv(msg_len).decode(self.__encoding_format)
                print(msg)

    def ready(self):
        receive_thread = threading.Thread(target=self.receive_msg)
        receive_thread.start()

        write_thread = threading.Thread(target=self.send_msg)
        write_thread.start()


if __name__ == '__main__':
    client = Client(server_ip_2con='192.168.120.1', port_ip_2con=15000)
    client.ready()
