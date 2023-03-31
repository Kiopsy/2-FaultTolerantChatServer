import socket
import threading
import multiprocessing
import time

class Server:
    def __init__(self, port, id, silent = False) -> None:
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.ID = id
        self.PORT = port
        self.SILENT = silent
        self.CONNECTION_WAIT = 5

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peers: dict[int, socket.socket] = {}
        for port in [50050, 50051, 50052]:
            self.peers[port] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.send_thread = threading.Thread(target=self.send_loop)
        self.stop_event = threading.Event()

        self.clients = []
        self.nicknames = []
    
    def sprint(self, body):
        if not self.SILENT:
            print(f"{self.ID}: {body}")

    def serve(self):
        self.receiver.bind((self.HOST, self.PORT))
        self.receiver.listen()
        print(f"Server is listening at {self.HOST} : {self.PORT}....")
        self.receive_thread.start()
    
    def receive_loop(self):
        def handle_server(clientsocket, addr):
            try:
                while not self.stop_event.is_set():

                    # Receive the message from the client
                    data = clientsocket.recv(4)
                    if not data:
                        raise BrokenPipeError
                    
                    message: int = struct.unpack("i", data)[0]

                    # Add the message to the queue
                    self.message_queue.put(message)
            except (KeyboardInterrupt, BrokenPipeError, BrokenPipeError):
                self.sprint(addr[0] + ' disconnected unexpectedly')
            finally:
                # Close the client socket
                clientsocket.close()
                self.stop()

        while not self.stop_event.is_set():
            clientsocket, addr = self.receiver.accept()
            self.sprint(f"{addr[0]} has joined")
            threading.Thread(target = handle_server, args = (clientsocket, addr)).start()

    def connect(self):
        self.sprint(f"Connecting in {self.CONNECTION_WAIT} seconds...")
        time.sleep(self.CONNECTION_WAIT)
        self.sprint("Connecting now...")
        for port in self.peers.keys():
            while True:
                try:
                    self.peers[port].connect((self.HOST, port))
                    break
                except socket.error as msg:
                    self.sprint(f"Socket binding error: {msg}\nRetrying in 5 secs...")
                    self.peers[port] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    time.sleep(5)

    def send_loop(self):
        pass

    def stop(self):
        self.receiver.close()
        for sock in self.peers.values():
            sock.close()

def run_server(server_id):
    server = Server(server_id)
    server.serve()
    server.connect()
    server.send_loop.start()

if __name__ == '__main__':
    
    ids = [0, 1, 2]   
    ps = [multiprocessing.Process(target=run_server, args=(i, )) for i in ids]
    
    for p in ps:
        p.start()
    for p in ps:
        p.join() 

exit()
"""
===================
===================
===================
"""        
class Machine:
    HOST = "localhost"
    NUM_PROCESSES = 3
    CONNECTION_WAIT = 10

    def __init__(self, machine_id: int, silent: bool = False, clock_rate: int = None, log_dir: str = "logs") -> None:

        self.SILENT = silent

        self.MACHINE_ID = machine_id

        # Only allow for machine_ids between 1 and 3 inclusive
        if machine_id < 1 or machine_id > 3:
            self.pprint("Only create machines with ids between 1 and 3 inclusive")
            exit(1)
        

        # Create the message queue
        self.message_queue = queue.Queue()


        # Define the machine's port and the port of other processes
        self.PEER_PORTS = [50050, 50051, 50052]
        self.PORT = 50049 + self.MACHINE_ID
        self.PEER_PORTS.remove(self.PORT)
        
        # Initialize the socket for receiving messages
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize a dict where sockets for sending messagese are values, and the key's are the recipients' ports
        self.send_sockets: dict[int, socket.socket] = {}
        for port in self.PEER_PORTS:
            self.send_sockets[port] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Mark if socket is fully connected
        self.receive_connected = False
        self.send_connected = False

        # Define the threads for receiving and sending messages
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.send_thread = threading.Thread(target=self.send_loop)
        self.stop_event = threading.Event()
        
    
    def pprint(self, content, end = "\n"):
        if not self.SILENT:
            print(f"Machine {self.MACHINE_ID}: {content}", end= end)
    
    # Initialize connections and start sending process
    def run(self):
        self.connect()
        
        while not (self.send_connected and self.receive_connected):
           time.sleep(0.001)

        self.pprint("All connected; starting now")
        self.send_thread.start()

    # Stop machine
    def stop(self):
        self.receive_connected = self.send_connected = False
        self.close()
        self.stop_event.set()

    # Close all sockets and log files in machine
    def close(self):
        self.receive_socket.close()
        for sock in self.send_sockets.values():
            sock.close()

    # Connect to all other machines
    def connect(self):
        self.pprint(f"Connecting in {self.CONNECTION_WAIT} seconds...")
        self.receive_thread.start()
        time.sleep(self.CONNECTION_WAIT)
        self.pprint("Connecting now...")
        
        
        for port in self.PEER_PORTS:
            while True:
                try:
                    self.send_sockets[port].connect((self.HOST, port))
                    break
                except socket.error as msg:
                    self.pprint(f"Socket binding error: " + str(msg) + "\n" + "Retrying in 5 secs...")
                    time.sleep(5)

        self.send_connected = True

    # Start receiving and handling clients
    def receive_loop(self):

        self.receive_socket.bind((self.HOST, self.PORT))
        self.receive_socket.listen(self.NUM_PROCESSES - 1)
        
        for _ in range(self.NUM_PROCESSES - 1):
            # accepts a client socket request
            clientsocket, addr = self.receive_socket.accept()
            self.pprint(f"{addr[0]} has joined")
            threading.Thread(target = self.handle_client, args = (clientsocket, addr)).start()

        self.receive_connected = True

    def handle_client(self, clientsocket: socket.socket, addr) -> None:
        try:
            while not self.stop_event.is_set():

                # Receive the message from the client
                data = clientsocket.recv(4)
                if not data:
                    raise BrokenPipeError
                
                message: int = struct.unpack("i", data)[0]

                # Add the message to the queue
                self.message_queue.put(message)
        except (KeyboardInterrupt, BrokenPipeError, BrokenPipeError):
            self.pprint(addr[0] + ' disconnected unexpectedly')
        finally:
            # Close the client socket
            clientsocket.close()
            self.stop()

    def send_loop(self):
       # Send messages to other machines with random probabilities
       pass

# Creates machine with specified id via command terminal args
def create_machine(machine_id = None, clock_rate = None, silent = False) -> Machine:
    if machine_id == None:
        if len(sys.argv) != 2:
            print("Usage: python machine.py machine_id")
            exit(1)

        try:
            machine_id = int(sys.argv[1])
        except:
            print("Usage: python machine.py machine_id:int")
            exit(1)
    
    return Machine(machine_id, silent=silent, clock_rate=clock_rate)

def main(id=None, clock_rate = None):
    machine = create_machine(id, clock_rate)
    machine.run()

if __name__ == '__main__':
    main()
