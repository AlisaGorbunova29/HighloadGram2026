# server.py
import time
import grpc
from concurrent import futures
import logging
import queue
import threading

import messenger_pb2_grpc as pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessengerServer(pb2_grpc.MessengerServiceServicer):
    def __init__(self):
        self.clients = {}
        self._lock = threading.Lock()

    def ChatStream(self, request_iterator, context):
        username = None
        msg_queue = queue.Queue()
        input_queue = queue.Queue(maxsize=100)

        def read_input():
            try:
                for msg in request_iterator:
                    input_queue.put(msg)
                    if not context.is_active():
                        break
            finally:
                input_queue.put(None)

        try:
            first_msg = next(request_iterator)
            username = first_msg.from_user

            with self._lock:
                self.clients[username] = msg_queue

            logger.info(f"Присоединился пользователь: {username}")

            threading.Thread(target=read_input, daemon=True).start()
            input_queue.put(first_msg)

            while context.is_active():
                try:
                    msg = input_queue.get(timeout=0.1)
                    if msg is None:
                        break 
                    self._handle_outgoing(msg)
                except queue.Empty:
                    pass

                try:
                    yield msg_queue.get_nowait()
                except queue.Empty:
                    pass

                time.sleep(0.01)

        finally:
            self._disconnect_user(username)

    def _handle_outgoing(self, msg):
        to_user = msg.to
        if to_user in self.clients:
            self.clients[to_user].put(msg)

    def _disconnect_user(self, username):
        if username:
            with self._lock:
                self.clients.pop(username, None)
            logger.info(f"Пользователь отключился: {username}")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MessengerServiceServicer_to_server(MessengerServer(), server)
    server.add_insecure_port('[::]:8010')
    logger.info("Сервер запушен на порту 8010")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        logger.info("Сервер остановлен")
        server.stop(0)


if __name__ == '__main__':
    serve()