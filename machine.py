import os
import grpc
import chat_service_pb2
import chat_service_pb2_grpc
import time
import threading
from thread_safe_set import ThreadSafeSet

LOGS_DIR = "logs"
HOST = "localhost"
HEARTRATE = 1

class Machine(chat_service_pb2_grpc.ChatServiceServicer):

    def __init__(self, id, silent = False):
        self.MACHINE_ID = id
        self.SILENT = silent
        self.primary_port = -1 
        self.connected = False

        self.HOST = HOST # change later
        self.PORT = 50050 + self.MACHINE_ID
        
        self.PEER_PORTS : dict[int, str] = {50050: HOST, 50051: HOST, 50052: HOST} # change "HOST" when we want to use other devices
        del self.PEER_PORTS[self.PORT]

        self.peer_alive = {port: False for port in self.PEER_PORTS}

        self.peer_stubs : dict[int, chat_service_pb2_grpc.ChatServiceStub] = {}

        self.heartbeat_thread = threading.Thread(target = self.receiveHeartbeat, daemon=True)

        # Create the log file
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.LOG_FILE_NAME = f"{LOGS_DIR}/machine{self.MACHINE_ID}.log"
        self.log_file = open(self.LOG_FILE_NAME , "w")
        self.log_dict = dict()

        # Voting
        self.seen_ballots = ThreadSafeSet()

    # Function for printing from within a machine
    def sprint(self, *args, end = "\n"):
        if not self.SILENT:
            print(f"Machine {self.MACHINE_ID}: {' '.join(str(x) for x in args)}", end = end)


    # PEER CONNECTIONS

    def connect(self):
        if not self.connected:
            try:
                for port, host in self.PEER_PORTS.items():
                    channel = grpc.insecure_channel(host + ':' + str(port)) 
                    self.peer_stubs[port] = chat_service_pb2_grpc.ChatServiceStub(channel)
                    revive_info = self.peer_stubs[port].Alive(chat_service_pb2.Empty())
                    
                    if revive_info.updates:
                        self.revive(revive_info)

                    self.peer_alive[port] = True
                self.connected = True
            except:
                raise Exception("Incorrect hostname or port")

        self.sprint("Connected")
        return self.connected

    def revive(self, revive_info):
        self.primary_port = revive_info.primary_port

        self.sprint("Received primary: ", self.primary_port)

        # clear log file and rewrite with revive_info file !!
        self.log_file.truncate(0)
        self.log_file.write(revive_info.commit_log)
        self.log_file.flush()

        # update db to be like the log file OR use binary sent data to be the new db
    
    def Alive(self, request, context):
        if self.primary_port == self.PORT:
            with open(self.LOG_FILE_NAME, 'r') as file:
                text_data = file.read()
            return chat_service_pb2.ReviveInfo(
                primary_port = self.primary_port, 
                commit_log = text_data, 
                db_bytes = bytes(),
                updates = True)
        else:
            return chat_service_pb2.ReviveInfo(updates = False)
    
    # HEARTBEAT

    def leaderElection(self):
        leader = float("inf")
        for port, alive in list(list(self.peer_alive.items()) + [(self.PORT, True)]):
            if alive:
                leader = min(leader, port)

        self.primary_port = leader
        self.sprint(f"New primary: {self.primary_port}")
    
    def receiveHeartbeat(self):
        if self.primary_port == -1:
            self.leaderElection() # is this safe to do (for rebooters)
        while True:
            time.sleep(HEARTRATE)
            for port, stub in self.peer_stubs.items():
                try:
                    response : chat_service_pb2.HeartbeatResponse = stub.RequestHeartbeat(chat_service_pb2.Empty())
                    self.peer_alive[response.port] = True
                    # self.sprint(f"Heartbeat received from port {port}")
                except:
                    if self.peer_alive[port]:
                        self.sprint(f"Heartbeat not received from port {port}")
                    self.peer_alive[port] = False
                    if self.primary_port == port: # if primary just died
                        self.leaderElection()
    
    def RequestHeartbeat(self, request, context):
        return chat_service_pb2.HeartbeatResponse(port=self.PORT)

    # CONSENSUS VOTING

    def sendCommitProposal(self, commit):

        ballot_id = self.seen_ballots.max() + 1
        self.seen_ballots.add(ballot_id)
        
        approved = True
        living_stubs = lambda: [(self.peer_stubs[port], port) for port in self.peer_alive if self.peer_alive[port]]

        for stub, port in living_stubs():
            req = chat_service_pb2.CommitRequest(commit = commit, ballot_id = ballot_id)
            try:
                response : chat_service_pb2.CommitVote = stub.ProposeCommit(req)
            except:
                self.peer_alive[port] = False
            approved &= response.approve

        for stub, port in living_stubs():
            vote = chat_service_pb2.CommitVote(commit = commit, approve = approved, ballot_id = ballot_id)
            try:
                stub.SendVoteResult(vote)
            except:
                self.peer_alive[port] = False

        if approved:
            # add commit
            self.writeToLog(commit, ballot_id)
        else:
            self.sprint("*Rejected commit")

        return approved

    def writeToLog(self, commit, ballot_id):
        # TODO: if not connected, wait until connected to add these commits
        self.sprint(f"Added commit {commit} w/ ballot_id {ballot_id}")
        self.log_file.write(f"{ballot_id}# {commit}\n")
        self.log_file.flush()

    def ProposeCommit(self, request, context):
        approved = request.ballot_id not in self.seen_ballots
        self.seen_ballots.add(request.ballot_id)
        return chat_service_pb2.CommitVote(approve = approved)
    
    def SendVoteResult(self, request, context):
        if request.approve:
            # add commit
            commit, ballot_id = request.commit, request.ballot_id
            self.writeToLog(commit, ballot_id)
        else:
            self.sprint("Rejected commit")

        return chat_service_pb2.Empty()

    # CLIENT FUNCTIONS
    def connection_required(func):
        def wrapper(self, request, context):

            if not self.connected:
                context.set_details("Server currently disconnected.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return grpc.RpcMethodHandler()
            
            return func(self, request, context)
        
        return wrapper
    
    @connection_required
    def Ping(self, request, context):
        return chat_service_pb2.Empty()

    @connection_required
    def Addition(self, request, context):

        self.sprint("Received addition request")

        sum = request.a + request.b

        success = False
        for i in range(5):
            self.sprint(i)
            if self.sendCommitProposal(f"{self.MACHINE_ID} -> {sum}"):
                success = True
                break
        
        self.sprint("Voting result", success)

        if success:
            return chat_service_pb2.Sum(sum = sum)
        else:
            return chat_service_pb2.Sum(sum = 0)