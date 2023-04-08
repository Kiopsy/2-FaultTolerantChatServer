import os
import grpc
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
import time
import threading

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
        
        # PEERS
        self.PEER_PORTS : dict[int, str] = {50050: HOST, 50051: HOST, 50052: HOST} # change "HOST" when we want to use other devices
        del self.PEER_PORTS[self.PORT]

        self.peer_alive : dict[int, bool] = {}
        self.peer_stubs : dict[int, chat_service_pb2_grpc.ChatServiceStub] = {}

        # LOGS
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.log_file = open(f"{LOGS_DIR}/machine{self.MACHINE_ID}.log", "r+")
        self.db = {}

        # VOTING
        self.in_voting = False
        self.proposed_commit = None
        self.proposed_line = None
        self.proposal_queue = []

        self.heartbeat_thread = threading.Thread(target = self.receiveHeartbeat, daemon=True)

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
        for port, alive in list(list(self.peer_alive.items()) + [(self.PORT, True)]):
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
                    self.sprint(f"Heartbeat received from port {response.port}")
                except:
                    self.peer_alive[port] = False
                    if self.primary == port: # if primary just died
                        self.leaderElection()
                    self.sprint(f"Heartbeat not received from port {port}")
    
    def RequestHeartbeat(self, request, context):
        super().ReceiveHeartbeat(request, context)
        return chat_service_pb2.HeartbeatResponse(port= self.PORT)

    def sendCommitProposal(self, commit, line):

        if self.in_voting:
            # wait until not voting
            pass


        self.in_voting = True
        votes = []
        for stub in [self.peer_stubs for port in self.peer_alive if self.peer_alive[port]]:
            response : chat_service_pb2.CommitVote = stub.ProposeCommit(chat_service_pb2.CommitRequest(commit = commit, line = line))
            votes.append(response.approve)
        
        print("Votes: ", votes)

        for stub in [self.peer_stubs for port in self.peer_alive if self.peer_alive[port]]:
            stub.VoteResult(chat_service_pb2.CommitVote(commit = commit, approve = all(votes), line = line))

    def ProposeCommit(self, request, context):
        super().ProposeCommit(request, context)

        approved =  request.line > len(self.log_file)
        return chat_service_pb2.CommitVote(chat_service_pb2.CommitVote(commit = "", approve = approved, line = -1))
        
            
    def VoteResult(self, request, context):
        super().VoteResult(request, context)

        if request.approve:
            # add commit
            commit, line = request.commit, request.line
            self.sprint(f"Added commit {commit} on line {line}")
        else:
            # remove commit
            self.sprint("Remove commit")

        self.is_voting = False
        return chat_service_pb2.Empty()
    

    def acceptCommit(self):
        pass
    
    def writeToDatabase(self):
        pass

    def log(self):
        # Open the file and count the number of lines
        self.sprint(len(self.log_file.readall()))

        