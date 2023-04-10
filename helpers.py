import threading, grpc, chat_service_pb2_grpc, chat_service_pb2
from concurrent import futures


SERVER_IPS = {50050: "10.250.174.43", 50051: "10.250.78.119", 50052: "10.250.78.119"}

class TwoFaultStub:
    def __init__(self):
        self.stub = None
        self.SERVERS = SERVER_IPS

    def connect(self) -> bool:
        for port, host in self.SERVERS.items():
            try:
                channel = grpc.insecure_channel(host + ':' + str(port)) 
                self.stub = chat_service_pb2_grpc.ChatServiceStub(channel)

                if not channel._channel.is_active():
                    raise Exception

                print(f"Client connected to machine w/ port {port}")
                return True
            except:
                print(f"Could not connect to {host}:{port}")
        
        return False
    
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            for _ in range(3):
                try:
                    func = getattr(self.stub, name)
                    response = func(*args, **kwargs)
                    return response
                except grpc.RpcError as e:
                    print(f"An error occurred while calling {name}: {e}")
                    self.connect()
                    
            print("No servers online")
            exit(0)
        return wrapper
        

class ThreadSafeSet:
    def __init__(self):
        self._set = set()
        self._lock = threading.Lock()
        self._max = 0
    
    def max(self):
        with self._lock:
            return self._max

    def add(self, item):
        with self._lock:
            self._set.add(item)
            self._max = max(self._max, item)

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
        
