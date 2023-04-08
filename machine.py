import os
import grpc
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
import time
import threading
import queue
from atom import Counter

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

        self.peer_alive = {}

        self.peer_stubs : dict[int, chat_service_pb2_grpc.ChatServiceStub] = {}

        self.heartbeat_thread = threading.Thread(target = self.receiveHeartbeat, daemon=True)

        # Create the log file
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.log_file = open(f"{LOGS_DIR}/machine{self.MACHINE_ID}.log", "w")

        # Voting
        self.proposal_queue = queue.Queue()
        self.proposals_count = Counter()
        self.in_voting = False

    def sprint(self, *args, end = "\n"):
        if not self.SILENT:
            print(f"Machine {self.MACHINE_ID}: {' '.join(str(x) for x in args)}", end = end)

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
                    self.sprint(f"Heartbeat received from port {port}")
                except:
                    self.peer_alive[port] = False
                    if self.primary == port: # if primary just died
                        self.leaderElection()
                    self.sprint(f"Heartbeat not received from port {port}")
    
    def RequestHeartbeat(self, request, context):
        return chat_service_pb2.HeartbeatResponse(port=self.PORT)
    
    def handleProposals(self):
        # Thread to handle proposals
        while True:
            if self.in_voting == True or self.proposal_queue.qsize() == 0:
                continue

            self.sendCommitProposal()

    # def voting_procedure(func):
    #     def wrapper(*args, **kwargs):
    #         self = args[0]
    #         func(*args, **kwargs)

    #     return wrapper
    
    def sendCommitProposal(self, commit, line):
        self.in_voting = True

        approved = True
        living_stubs = lambda: [self.peer_stubs[port] for port in self.peer_alive if self.peer_alive[port]]

        for stub in living_stubs():
            req = chat_service_pb2.CommitRequest(commit = commit, line = line)
            response : chat_service_pb2.CommitVote = stub.ProposeCommit(req)
            approved &= response.approve

        for stub in living_stubs():
            vote = chat_service_pb2.CommitVote(commit = commit, approve = approved, line = line)
            stub.SendVoteResult(vote)

        if approved:
            # add commit
            self.sprint(f"Added commit {commit} on line {line}")
        else:
            self.sprint("Rejected commit")

        self.in_voting = False
        return approved

    def writeToLog(self, commit, line):
        self.log_file.write(commit)
        nums = commit.split(';')

    def ProposeCommit(self, request, context):
        self.in_voting = True

        approved = request.line >= 0#len(self.log_file)
        return chat_service_pb2.CommitVote(approve = approved)
    
    def SendVoteResult(self, request, context):
        self.in_voting = True

        if request.approve:
            # add commit
            commit, line = request.commit, request.line
            self.sprint(f"Added commit {commit} on line {line}")
        else:
            self.sprint("Rejected commit")

        self.is_voting = False
        return chat_service_pb2.Empty()
    
    def Addition(self, request, context):
        return chat_service_pb2.Sum(sum = request.a + request.b)