import grpc
from concurrent import futures
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
from machine import Machine
import multiprocessing
import time
import random

def serve(id):
    machine = Machine(id)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_service_pb2_grpc.add_ChatServiceServicer_to_server(machine, server)
    server.add_insecure_port(machine.HOST + ':' + str(machine.PORT))
    server.start()

    machine.sprint("Server initialized at " + machine.HOST)
    machine.sprint(f"Port: {machine.PORT}")

    time.sleep(3)
    machine.connect()
    machine.heartbeat_thread.start()
    for i in range(5):
        num = random.randint(1,3)
        time.sleep(num)
        machine.sendCommitProposal(commit = f"{machine.MACHINE_ID}: {i} -- {num}", line = 1)
    server.wait_for_termination()


if __name__ == '__main__':
    NUM_SERVERS = 3
    processes: list[multiprocessing.Process] = []
    
    # Spawns a new process for each machine that we have to run 
    for i in range(NUM_SERVERS):
        process = multiprocessing.Process(target=serve, args=(i, ))
        processes.append(process)

    for process in processes:
        process.start()

    # for process in processes:
    #     process.join()

    print("Three servers created using multiprocessing.")

    # time.sleep(5)
    # # Kill the first process
    # processes[0].terminate()
    # for i in range(10):
    #     print('first process killed')