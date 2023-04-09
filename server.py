import grpc
from concurrent import futures
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
from machine import Machine
import multiprocessing
import time
import random
import signal, sys

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
    #### TESTIING MULTIPLE COMMITS AT ONCE
    for i in range(5):
        num = random.randint(1,3)
        time.sleep(num)
        machine.sendCommitProposal(commit = f"machine {machine.MACHINE_ID}, commit {i}")
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
    print("Three servers created using multiprocessing.")
    
    ### Clean exiting on ^C
    def signal_handler(signal, frame):
        for p in processes:
            p.terminate()
        print("Exiting...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    for _ in range(5):
        #### TESTING KILLING THE FIRST PROCESS
        time.sleep(8)
        choices = input("Which process id(s) should die: ")
        choices = choices.split(", ")
        choices = [int(c) for c in choices]

        for c in choices:
            processes[c].terminate()
            for _ in range(3):
                print(f'Machine {c} killed')

        time.sleep(8)

        #### TESTING REVIVING THE FIRST PROCESS
        for c in choices:
            multiprocessing.Process(target=serve, args=(c, )).start()