import grpc
import chat_service_pb2
import chat_service_pb2_grpc
import threading
import time
import random

HOST = "localhost"
MESSAGE_RATE = 3

class Client:
    def __init__(self) -> None:
        self.servers = {50050: HOST, 50051: HOST, 50052: HOST}
        self.stub = None
        self.connected = False
        self.send_thread = threading.Thread(target=self.sendAddition, daemon=True)

    def connect(self):
        for port, host in self.servers.items():
            try:
                channel = grpc.insecure_channel(host + ':' + str(port)) 
                self.stub = chat_service_pb2_grpc.ChatServiceStub(channel)
                self.stub.Ping(chat_service_pb2.Empty())

                self.connected = True
                print(f"Client connected to machine w/ port {port}")
                break
            except:
                print("Could not connect")
                pass

    def sendAddition(self):
        while self.connected:
            a = int(input("A: "))
            b = int(input("B: "))

            while True:
                try:
                    numbers = chat_service_pb2.TwoNumbers(a=a, b=b)
                    sum = self.stub.Addition(numbers).sum

                    print(f"Server finished our addition request: {sum}")
                    break
                except Exception as e:
                    # handle the exception and print the error message
                    print(f"An error occurred")
                    self.connect()


if __name__ == '__main__':

    print("Server addition application!")
    client = Client()
    client.connect()
    client.sendAddition()


