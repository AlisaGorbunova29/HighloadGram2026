import grpc
import time
import logging
import sys
import threading

import messenger_pb2 as pb2
import messenger_pb2_grpc as pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessengerClient:
    def __init__(self, username, server_url="localhost:8010"):
        self.username = username
        self.channel = grpc.insecure_channel(server_url)
        self.stub = pb2_grpc.MessengerServiceStub(self.channel)
        self.running = False
        self.input_queue = []

    def start_chat(self):
        self.running = True
        
        input_thread = threading.Thread(target=self._input_loop, daemon=True)
        input_thread.start()
        
        def message_generator():

            connect_msg = pb2.Message(
                from_user=self.username,
                to=self.username,
                content="__CONNECT__"
            )
            yield connect_msg
            
            while self.running:
                if self.input_queue:
                    message = self.input_queue.pop(0)
                    yield message
                else:
                    time.sleep(0.01)

        try:
            for response in self.stub.ChatStream(message_generator()):
                if hasattr(response, 'from_user') and hasattr(response, 'content'):
                    print(f"\r{response.from_user}: {response.content}\n{self.username}: ", end="")
                
        finally:
            self.running = False

    def _input_loop(self):
        while self.running:
            try:
                text = input(f"{self.username}> ")
                
                if text.strip().lower() == "quit":
                    self.running = False
                    break
                
                to, *body = text.split(" ", 1)
                message = pb2.Message(
                    from_user=self.username,
                    to=to,
                    content=" ".join(body)
                )
                
                self.input_queue.append(message)
                
            except EOFError:
                self.running = False
                break
        
        self.running = False

    def close(self):
        self.running = False
        self.channel.close()

if __name__ == '__main__':
    client = MessengerClient(sys.argv[1])
    print(f"Добро пожаловать в HighloadGram!\nФормат сообщений: $никнейм_пользователя $сообщение\nВыход: quit\n\n")
    try:
        client.start_chat()
    finally:
        client.close()