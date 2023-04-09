import os
import grpc
import chat_service_pb2
import chat_service_pb2_grpc
import time
import threading

LOGS_DIR = "logs"
HOST = "localhost"
HEARTBEAT_RATE = 1

class ThreadSafeSet:
    def __init__(self):
        self._set = set()
        self._lock = threading.Lock()

    def add(self, item):
        with self._lock:
            self._set.add(item)

    def remove(self, item):
        with self._lock:
            self._set.remove(item)

    def __contains__(self, item):
        with self._lock:
            return item in self._set

    def __len__(self):
        with self._lock:
            return len(self._set)
        
    def __iter__(self):
        with self._lock:
            return iter(self._set)

# class ExceptionBlocker:
#     def __init__(self, stub):
#         self.stub = stub
        
#     def __getattr__(self, name):
#         method = getattr(self.stub, name)
#         def wrapper(*args, **kwargs):
#             try:
#                 return method(*args, **kwargs)
#             except grpc.RpcError as e:
#                 print(f"Error calling {name}: {e}")
#         return wrapper

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

        self.peer_alive = {port: False for port in self.PEER_PORTS}

        self.peer_stubs : dict[int, chat_service_pb2_grpc.ChatServiceStub] = {}

        self.heartbeat_thread = threading.Thread(target = self.receiveHeartbeat, daemon=True)

        # Create the log file
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.log_file = open(f"{LOGS_DIR}/machine{self.MACHINE_ID}.log", "w")
        self.log_dict = dict()


        # Voting
        self.in_voting = False
        self.seen_ballots = ThreadSafeSet()

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
                    self.peer_stubs[port].Ping(chat_service_pb2.Empty())
                    self.peer_alive[port] = True
                self.connected = True
            except:
                raise Exception("Incorrect hostname or port")

        self.sprint("Connected")
        return self.connected       

    
    # HEARTBEAT

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
                    # IF PEER WAS dead, primary should send over the log file -> the peer will respond when its rebooted its db -> and then will be allowed to come back to life
                    # if self.peer_alive[port] == False:
                    #     self.reconnect(port)
                    self.peer_alive[response.port] = True
                    # self.sprint(f"Heartbeat received from port {port}")
                except:
                    self.peer_alive[port] = False
                    if self.primary == port: # if primary just died
                        self.leaderElection()
                    self.sprint(f"Heartbeat not received from port {port}")
    
    def RequestHeartbeat(self, request, context):
        return chat_service_pb2.HeartbeatResponse(port=self.PORT)

    # CONSENSUS VOTING

    def sendCommitProposal(self, commit):

        ballot_id = max(self.seen_ballots if self.seen_ballots else [0]) + 1
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
    

    def Ping(self, request, context):
        return chat_service_pb2.Empty()

    # CLIENT FUNCTIONS

    def connection_required(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if not self.connected:
                return
            
            func(*args, **kwargs)
        
        return wrapper

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