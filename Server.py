import socket
import threading
import attr


@attr.s
class Server:
    _port: int = attr.ib(default=15000, init=True)
    _host_ip: str = attr.ib(default=None, init=True)
    _tcp: bool = attr.ib(default=True, init=True)
    __server: socket.socket = attr.ib(default=None, init=False)
    __is_running: bool = attr.ib(default=False, init=False)
    __header_len: int = attr.ib(default=1024, init=False)
    __encoding_format: str = attr.ib(default="utf-8", init=False)
    __clients: list = attr.ib(default=[], init=False)
    __user_names: list = attr.ib(default=[], init=False)

    def __attrs_post_init__(self) -> None:
        address = (self._host_ip, self._port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(address)

    def send_info(self, client: socket.socket, info: str):
        message = info.encode(self.__encoding_format)
        msg_len = len(message)
        send_len = str(msg_len).encode(self.__encoding_format)
        send_len += b' ' * (self.__header_len - len(send_len))
        print(send_len)
        client.send(send_len)
        client.send(message)

    def get_username(self, client: socket.socket) -> None:
        username_len = client.recv(self.__header_len).decode(self.__encoding_format)
        print(username_len)

        username_len = int(username_len)

        username = client.recv(username_len).decode(self.__encoding_format)
        self.__user_names.append(username)
        self.__clients.append(client)
        message = f'{username} joined the room!'
        self.broadcast_2_clients(message)

    def broadcast_2_clients(self, message: str) -> None:
        for client in self.__clients:
            self.send_info(client=client, info=message)

    def handle_client(self, client: socket.socket, client_ip: str) -> None:
        print(f"New Connection {client_ip} connected.")

        while True:
            try:
                msg_len = client.recv(self.__header_len).decode(self.__encoding_format)
                if msg_len:
                    msg_len = int(msg_len)
                    msg = client.recv(msg_len).decode(self.__encoding_format)
                    self.broadcast_2_clients(message=msg)

            except ConnectionResetError or OSError or ValueError:
                index = self.__clients.index(client)
                self.__clients.remove(client)
                client.close()
                username = self.__user_names[index]
                broadcast_msg = f'{username} left the room.'
                self.broadcast_2_clients(broadcast_msg)
                self.__user_names.remove(username)

    def run_client_conn(self, client, client_ip):
        thread = threading.Thread(target=self.handle_client, args=(client, client_ip))
        thread.start()

    def start_listening(self) -> None:
        if self.__is_running:
            print("Server is already listening")
        else:
            print("Server is listening...")
            self.server.listen()
            while True:
                client, client_ip = self.server.accept()  # conn = object to communicate back
                self.get_username(client)
                self.run_client_conn(client, client_ip)


if __name__ == '__main__':
    s = Server(host_ip='192.168.120.1', port=15000)
    s.start_listening()
