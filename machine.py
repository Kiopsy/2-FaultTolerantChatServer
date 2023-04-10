import os, grpc, time, threading, socket
import chat_service_pb2
from chat_service_pb2_grpc import ChatServiceServicer, ChatServiceStub
from thread_safe_set import ThreadSafeSet

LOGS_DIR = "logs"
HOST = "localhost"
HEARTRATE = 1

class Machine(ChatServiceServicer):

    def __init__(self, id, silent = False) -> None:
        # initialize constants 
        self.MACHINE_ID = id
        self.SILENT = silent

        # initialize channel constants
        self.HOST = HOST # change later
        self.PORT = 50050 + self.MACHINE_ID

        # dict of the other servers' ports -> their host/ips
        self.PEER_PORTS : dict[int, str] = {50050: HOST, 50051: HOST, 50052: HOST} # change "HOST" when we want to use other devices
        del self.PEER_PORTS[self.PORT]

        # dict of the other servers' ports -> bool determining if they are alive
        self.peer_alive = {port: False for port in self.PEER_PORTS}
        self.peer_stubs : dict[int, ChatServiceStub] = {}

        # identifies the leading server's port number
        self.primary_port = -1 
        
        # bool dictating if the current server is connected to the other (living) ones
        self.connected = False
        
        # thread to look for heartbeats from the other servers
        self.heartbeat_thread = threading.Thread(target = self.receive_heartbeat, daemon=True)
        self.stop_event = threading.Event()

        # initialization of the commit log file
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.LOG_FILE_NAME = f"{LOGS_DIR}/machine{self.MACHINE_ID}.log"
        self.log_file = open(self.LOG_FILE_NAME , "w")
        
        # thread safe set that tracks if a ballot id has been seen
        self.seen_ballots = ThreadSafeSet()

    # func "sprint": prints within a machine
    def sprint(self, *args, end = "\n") -> None:
        if not self.SILENT:
            print(f"Machine {self.MACHINE_ID}: {' '.join(str(x) for x in args)}", end = end)

    # (RE)CONNECTION SECTION

    # func "connect": connect current machine to peers
    def connect(self) -> bool:
        if not self.connected:
            # Form a connection (stub) between all other peers (if they are alive)
            for port, host in self.PEER_PORTS.items():
                try:
                    # form connection (stub)
                    channel = grpc.insecure_channel(host + ':' + str(port)) 
                    self.peer_stubs[port] = ChatServiceStub(channel)
                    #  check if the peer is alive
                    revive_info = self.peer_stubs[port].Alive(chat_service_pb2.Empty())
                    # if the peer has updates to share, update the current machine
                    if revive_info.updates:
                        self.update(revive_info)

                    self.peer_alive[port] = True
                except:
                    self.peer_alive[port] = False

            self.connected = True

        self.sprint("Connected")
        return self.connected

    # func "update": incorporate the receieved revive info
    def update(self, revive_info) -> None:
        self.primary_port = revive_info.primary_port

        self.sprint("Received primary: ", self.primary_port)

        # clear log file and rewrite with revive_info file !!
        self.log_file.truncate(0)
        self.log_file.write(revive_info.commit_log)
        self.log_file.flush()

        # update db to be like the log file OR use binary sent data to be the new db
        # TODO
    
    # rpc func "Alive": takes in Empty and returns updates (if it is the primary machine) or no updates
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
    
    # HEARTBEAT SECTION

    # func "leader_election": uses the bully algorithm to elect the machine with the lowest port as the leader
    def leader_election(self) -> int:
        alive_ports = (port for port, alive in [*self.peer_alive.items(), (self.PORT, True)] if alive)
        self.primary_port = min(alive_ports)
        self.sprint(f"New primary: {self.primary_port}")
        return self.primary_port
    
    # func "receive_heartbeat": ask all other machines if they are alive by asking of
    def receive_heartbeat(self) -> None:
        # elect leading machine if none
        if self.primary_port == -1:
            self.leader_election()

        # every HEARTRATE seconds, ask for all heartbeats
        while not self.stop_event.is_set():
            time.sleep(HEARTRATE)
            for port, stub in self.peer_stubs.items():
                try:
                    response : chat_service_pb2.HeartbeatResponse = stub.RequestHeartbeat(chat_service_pb2.Empty())
                    self.peer_alive[response.port] = True
                except:
                    # if cannot connect to a peer, mark it as dead
                    if self.peer_alive[port]:
                        self.sprint(f"Heartbeat not received from port {port}")
                    self.peer_alive[port] = False
                    if self.primary_port == port: # run an election if the primary has died 
                        self.leader_election()
    
    # func "stop_machine": stop the machine's heartbeat by setting stop_event
    def stop_machine(self):
        self.stop_event.set() 
        self.heartbeat_thread.join()

    # rpc func "RequestHeartbeat": takes Empty as input and retuns its port
    def RequestHeartbeat(self, request, context):
        return chat_service_pb2.HeartbeatResponse(port=self.PORT)

    # CONSENSUS VOTING SECTION

    # func "send_commit_proposal" : proposes a commit, if all peers agree on it: it is commited; else: it is rejected
    def send_commit_proposal(self, commit) -> bool:

        # sets the ballot id to the largest unseen ballot
        ballot_id = self.seen_ballots.max() + 1
        self.seen_ballots.add(ballot_id)
        
        approved = True
        living_stubs = lambda: [(self.peer_stubs[port], port) for port in self.peer_alive if self.peer_alive[port]]

        # sends the commit request to all living peers and tallies their responses
        for stub, port in living_stubs():
            req = chat_service_pb2.CommitRequest(commit = commit, ballot_id = ballot_id)
            try:
                response : chat_service_pb2.CommitVote = stub.ProposeCommit(req)
            except:
                self.peer_alive[port] = False
            approved &= response.approve

        # sends the result of the vote to all living peers
        for stub, port in living_stubs():
            vote = chat_service_pb2.CommitVote(commit = commit, approve = approved, ballot_id = ballot_id)
            try:
                stub.SendVoteResult(vote)
            except:
                self.peer_alive[port] = False

        # commits changes if vote was approved
        if approved:
            # add commit
            self.write_to_log(commit, ballot_id)
        else:
            self.sprint("*Rejected commit")

        return approved

    # func "write_to_log": writes a commit to the log file
    def write_to_log(self, commit, ballot_id):
        # TODO: if not connected, wait until connected to add these commits
        self.sprint(f"Added commit {commit} w/ ballot_id {ballot_id}")
        self.log_file.write(f"{ballot_id}# {commit}\n")
        self.log_file.flush()

    # rpc func "ProposeCommit": takes a CommitRequest/Proposal as input, returns an approving vote iff the ballot id is unseen
    def ProposeCommit(self, request, context):
        approved = request.ballot_id not in self.seen_ballots
        self.seen_ballots.add(request.ballot_id)
        return chat_service_pb2.CommitVote(approve = approved)
    
    # rpc func "SendVoteResult": takes a CommitVote/Final verdict as input, adds commit if approved, returns Empty
    def SendVoteResult(self, request, context):
        if request.approve:
            # add commit
            commit, ballot_id = request.commit, request.ballot_id
            self.write_to_log(commit, ballot_id)
        else:
            self.sprint("Rejected commit")

        return chat_service_pb2.Empty()

    # CLIENT FUNCTIONS SECTION

    # decorator that only allows clients to connect if the current machine is connected to the peers
    def connection_required(func):
        def wrapper(self, request, context):

            if not self.connected:
                context.set_details("Server currently disconnected.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return grpc.RpcMethodHandler()
            
            return func(self, request, context)
        
        return wrapper
    
    # rpc func "Ping": confirms a machine is alive; Empty -> Empty
    @connection_required
    def Ping(self, request, context):
        return chat_service_pb2.Empty()

    # rpc func "Addition": adds 2 numbers; TwoNumbers -> Sum
    @connection_required
    def Addition(self, request, context):

        self.sprint("Received addition request")

        sum = request.a + request.b

        success = False
        for i in range(5):
            self.sprint(i)
            if self.send_commit_proposal(f"{self.MACHINE_ID} -> {sum}"):
                success = True
                break
        
        self.sprint("Voting result", success)

        if success:
            return chat_service_pb2.Sum(sum = sum)
        else:
            return chat_service_pb2.Sum(sum = 0)