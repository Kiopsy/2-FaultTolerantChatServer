import os
import grpc
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
import time

LOGS_DIR = "logs"
HOST = "localhost"
HEARTBEAT_RATE = 1

class Machine(chat_service_pb2_grpc.ChatServiceServicer):

    def __init__(self, id, silent = False):
        self.MACHINE_ID = id
        self.SILENT = silent
        self.primary = -1
        self.connected = False

        self.HOST = HOST # change later
        self.PORT = 50050 + self.MACHINE_ID
        
        self.PEER_PORTS : dict[int, str] = {50050: HOST, 50051: HOST, 50052: HOST} # change "HOST" when we want to use other devices
        del self.PEER_PORTS[self.PORT]

        self.peer_alive : dict[int, bool] = {} # change "HOST" when we want to use other devices

        self.peer_stubs : dict[int, chat_service_pb2_grpc.ChatServiceStub] = {}

        # Create the log file
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.log_file = open(f"{LOGS_DIR}/machine{self.MACHINE_ID}.log", "w")

    def sprint(self, body, end = "\n"):
        if not self.SILENT:
            print(f"Machine {self.MACHINE_ID}: {body}", end = end)

    def connect(self):
        if not self.connected:
            try:
                for port, host in self.PEER_PORTS.items():
                    channel = grpc.insecure_channel(host + ':' + str(port)) 
                    self.peer_stubs[port] = chat_service_pb2_grpc.ChatServiceStub(channel)
                    self.peer_alive[port] = True
                self.connected = True
            except:
                raise Exception("Incorrect hostname or port")

        self.sprint("Connected")
        return self.connected
    
    def leaderElection(self):
        leader = float("inf")
        for port, alive in list(self.peer_alive.items()) + [(self.PORT, True)]:
            if alive:
                leader = min(leader, port)

        self.primary = leader
        self.sprint(f"New primary: {self.primary}")
    
    def receiveHeartbeat(self):
        self.leaderElection()
        
        while True:
            time.sleep(HEARTBEAT_RATE)
            for port, stub in self.peer_stubs.items():
                try:
                    response : chat_service_pb2.HeartbeatResponse = stub.RequestHeartbeat(chat_service_pb2.Empty())
                    self.peer_alive[response.port] = True
                    self.sprint(f"Heartbeat received from port {port}")
                except:
                    self.peer_alive[port] = False
                    if self.primary == port: # if primary just died
                        self.leaderElection()
                    self.sprint(f"Heartbeat not received from port {port}")

    def RequestHeartbeat(self, request, context):
        super().ReceiveHeartbeat(request, context)
        return chat_service_pb2.HeartbeatResponse(port=self.PORT, primary=self.IS_PRIMARY)



