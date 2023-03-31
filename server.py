import multiprocessing
import grpc
from concurrent import futures
import backend.chat_service_pb2 as chat_service_pb2
import backend.chat_service_pb2_grpc as chat_service_pb2_grpc
from backend.database import Database
import socket
import pickle
import time
import os
from collections import defaultdict

# Save the db to pkl file after every update
def storeData(db):
    with open('./backend/db.pkl', 'wb') as dbfile:
        pickle.dump(db, dbfile)

# Load the db from pkl or create if non-existant
def loadData(filename):
    try:
        with open(filename, 'rb')  as dbfile:
            db = pickle.load(dbfile)
    except:
        return {"passwords" : dict(), "messages": defaultdict(list)}

db = loadData('./backend/db.pkl')

class Server:
    NUM_SERVERS = 3
    CONNECTION_WAIT = 10
    MAX_CLIENTS = 10

    def __init__(self, server_id: int, silent: bool = False):
        # Only allow for machine_ids between 1 and 3 inclusive
        if server_id < 1 or server_id > 3:
            self.pprint("Only create server with ids between 1 and 3 inclusive")
            os._exit(1)
        self.server_id = server_id                                                                                                                                                                                                                                                                                                  
        self.host = socket.gethostbyname(socket.gethostname())
        self.peer_ports = [50050, 50051, 50052]
        self.port = 50049 + self.server_id
        self.peer_ports.remove(self.port)
        self.peer_stubs = {}
        self.master = False # Master server in the system
        self.server = None

    def pprint(self, content, end = "\n"):
        if not self.SILENT:
            print(f"Server {self.server_id}: {content}", end= end)

    # Start gRPC server with both Chat and Auth servicers
    def serve(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.MAX_CLIENTS))
        chat_service_pb2_grpc.add_ChatServiceServicer_to_server(ChatServiceServicer(), self.server)
        self.server.add_insecure_port(self.host + ':' + str(self.port))
        self.server.start()
        self.pprint("Server initialized at " + self.host)
        try: 
            self.server.wait_for_termination()
        except KeyboardInterrupt: 
            print("Caught keyboard interruption exception, server exiting.")
        finally: 
            os._exit(1)

    # Connect to all other servers for interserver communication
    def connect(self):
        self.pprint(f"Connecting in {self.CONNECTION_WAIT} seconds...")
        time.sleep(self.CONNECTION_WAIT)
        self.pprint("Connecting now...")
        for port in self.peer_ports:
            try:
                channel = grpc.insecure_channel(self.host + ':' + str(port)) 
                self.peer_stubs[port] = chat_service_pb2_grpc.ChatServiceStub(self.channel)
            except:
                raise Exception("Incorrect hostname or port")

    # Select leader by lowest id
    def detectLeader(self):
        # Send heartbeats to other peer servers to detect failures
        if self.server_id == 1: 
            self.master = True

        # Send heartbeats
        # reset master    


            
class ChatServiceServicer(chat_service_pb2_grpc.ChatServiceServicer):

    # Checks if user can login based on request's credentials. Returns success/error
    def Login(self, request, context):
        username = request.username 
        password = request.password 
        # Check if username/password matches a registered user
        if username in db["passwords"] and password == db["passwords"][username]:
            return chat_service_pb2.LoginResponse(success=True, message='Login successful')
        else:
            return chat_service_pb2.LoginResponse(success=False, message='Invalid username or password')
    
    # Registers a user into our database. Returns success/error
    def Register(self, request, context):
        username = request.username
        password = request.password
        # Add the username/password to the database if not taken
        if username not in db["passwords"]:
            db["passwords"][username] = password
            storeData(db)
            # Send response success
            return chat_service_pb2.RegisterResponse(success=True, message='Register successful')
        else:
            # Send error to prevent multiple users registering
            return chat_service_pb2.RegisterResponse(success=False, message='This username is taken')
    
    # Deletes a user from the database Returns success/error
    def Delete(self, request, context):
        username = request.username
        # Delete username/password if account in database
        if request.username in db["passwords"]:
            del db["passwords"][username]
            del db["messages"][username]
            storeData(db)
            # Send response success
            return chat_service_pb2.DeleteResponse(success=True, message='Account deleted')
        else:
            # Send error
            return chat_service_pb2.DeleteResponse(success=False, message='Account does not exist')
        
    # Sends a message from a sender to a recipient based on request details. 
    def SendMessage(self, request, context):
        sender = request.sender
        recipient = request.recipient
        content = request.content

        # Return error code for invalid recipient/senders
        if sender not in db["passwords"] or recipient not in db["passwords"]:
            return chat_service_pb2.SendResponse(success = False, message = "Invalid sender or recipient. Does the sender/recipient exist?")

        # Store message in database and return success code
        print(f"Received message from {sender} to {recipient}: {content}")
        db["messages"][recipient].append(request)
        
        return chat_service_pb2.SendResponse(success = True, message = "Message sent")

    # Return the current users in the db.  
    def GetUsers(self, request, context):
        for user in db["passwords"]:
            yield chat_service_pb2.User(username = user)
    
    # Retrieve all messages made to a recipient, deleting as we go. 
    def ReceiveMessage(self, request, context):
        recipient = request.username 
        # Loop in reverse order to maintain order messages were received.
        for i in range(len(db["messages"][recipient]) - 1, -1, -1): 
            message = db["messages"][recipient][i]
            yield chat_service_pb2.ChatMessage(sender = message.sender, content = message.content)
            db["messages"][recipient].pop()
            storeData(db)

def run_server(server_id):
    server = Server(server_id)
    server.serve()
    server.connect()
        
if __name__ == '__main__':

    NUM_SERVERS = 3
    processes: list[multiprocessing.Process] = []
    
    # Spawns a new process for each machine that we have to run 
    for i in range(NUM_SERVERS):
        process = multiprocessing.Process(target=run_server, args=(i+1, ))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    print("Three servers created using multiprocessing.")