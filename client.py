import socket
import attr
import threading
import cv2
import pickle
import os


@attr.s(auto_attribs=True)
class ChatRoom:

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
        self.__client.sendall(username_len)
        self.__client.sendall(self.__username.encode(self.__encoding_format))
        print('Connected')

    def send_info(self, info):
        message = info.encode(self.__encoding_format)
        msg_len = len(message)
        send_len = str(msg_len).encode(self.__encoding_format)
        send_len += b' ' * (self.__header_len - len(send_len))
        self.__client.sendall(send_len)
        self.__client.sendall(message)

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


@attr.s
class ImageClient(object):

    _server_ip_2con: str = attr.ib(default=None, init=True)
    _port_ip_2con: int = attr.ib(default=None, init=True)
    __client: socket.socket = attr.ib(default=None, init=False)
    __encoding_format: str = attr.ib(default="utf-8", init=True)
    _resolution: int = attr.ib(default=480, init=True)
    __resolution_shape: tuple = attr.ib(default=((3, 640), (4, 480)), init=False)
    __header_len: int = attr.ib(default=1024, init=True)
    __frame_size_bytes: int = attr.ib(default=921765, init=False)

    @_resolution.validator
    def _check_x(self, attribute, value):
        if value not in [360, 480, 720]:
            raise ValueError("Video resolution must be 480p 720p or 1080p")

    def __attrs_post_init__(self) -> None:
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((self._server_ip_2con, self._port_ip_2con))

        if self._resolution == 360:
            self.__frame_size_bytes = 691365
            self.__resolution_shape = ((3, 640), (4, 360))
        elif self._resolution == 720:
            self.__frame_size_bytes = 2764965
            self.__resolution_shape = ((3, 1280), (4, 720))
        elif self._resolution == 1080:
            self.__frame_size_bytes = 6220965
            self.__resolution_shape = ((3, 1920), (4, 1080))

        # sending buffer size to be received by the server
        send_len = str(self.__frame_size_bytes).encode(self.__encoding_format)
        send_len += b' ' * (self.__header_len - len(send_len))
        self.__client.sendall(send_len)

    def send_vid(self, start_capturing: bool = True, quit_key: str = 'q'):
        if start_capturing:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            cap.set(self.__resolution_shape[0][0], self.__resolution_shape[0][1])
            cap.set(self.__resolution_shape[1][0], self.__resolution_shape[1][1])

            while True:
                ret, frame = cap.read()
                cv2.imshow('frame', frame)
                pick_frm = pickle.dumps(frame)
                self.__client.sendall(pick_frm)
                if cv2.waitKey(1) & 0xFF == ord(quit_key):
                    break

    def _send_local_vid(self, vid_name: str):
        cap = cv2.VideoCapture(vid_name)
        _, first_frame = cap.read()
        pickled_f = pickle.dumps(first_frame)
        pickled_len = len(pickled_f)
        send_len = str(pickled_len).encode(self.__encoding_format)
        send_len += b' ' * (self.__header_len - len(send_len))
        self.__client.sendall(send_len)

        while cap.isOpened():
            ret, frame = cap.read()
            pickled_frm = pickle.dumps(frame)
            self.__client.sendall(pickled_frm)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def send_img(self, img_name: str) -> None:
        img = cv2.imread(img_name)
        pickle_img = pickle.dumps(img)
        pickle_len = len(pickle_img)
        send_len = str(pickle_len).encode(self.__encoding_format)
        send_len += b' ' * (self.__header_len - len(send_len))
        self.__client.sendall(send_len)
        self.__client.sendall(pickle_img)

    def screen_share(self):



if __name__ == '__main__':
    # client = Client(server_ip_2con='192.168.120.1', port_ip_2con=15000)
    # client.ready()
    vi = ImageClient(server_ip_2con='192.168.120.1', port_ip_2con=15000, resolution=360)

