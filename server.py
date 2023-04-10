import grpc, signal, sys, multiprocessing, time, random
from concurrent import futures
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
from machine import Machine

NUM_SERVERS = 3

# func "random_commits": machine randomly proposes 5 commits in  
# TESTING: potentially simultaneous commit proposals
def random_commits(machine: Machine):
    for i in range(5):
        num = random.randint(1,3)
        time.sleep(num)
        machine.send_commit_proposal(commit = f"machine {machine.MACHINE_ID}, commit {i}")

# func "serve": 
def serve(id):
    machine = Machine(id)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_service_pb2_grpc.add_ChatServiceServicer_to_server(machine, server)
    server.add_insecure_port(machine.HOST + ':' + str(machine.PORT))
    server.start()

    machine.sprint(f"Server initialized at {machine.HOST} on port {machine.PORT}")

    time.sleep(3)
    machine.connect()
    machine.heartbeat_thread.start()
    server.wait_for_termination()

# func "create_processes": creates a list of processes that serve machines; None -> List[Process]
def create_processes() -> list[multiprocessing.Process]:
    processes = []
    
    # Spawns a new process for each machine that we have to run 
    for i in range(NUM_SERVERS):
        process = multiprocessing.Process(target=serve, args=(i, ))
        processes.append(process)
    
    return processes

# func "start_processes": starts a list of processes that serve machines; List[Process] -> None
def start_processes(processes: list[multiprocessing.Process]) -> None:
    for process in processes:
        process.start()

# func "kill_revive": kills process(es) and revives after 8 sec
# TESTING: kill and revive functionality
def kill_revive(processes: list[multiprocessing.Process]) -> None:
    choices = input("Which process id(s) should die: ")
    choices = choices.split(", ")
    choices = [int(c) for c in choices]

    # killing processes
    if choices:
        for c in choices:
            processes[c].terminate()
            for _ in range(3):
                print(f'Machine {c} killed')

    time.sleep(8)

    # reviving processes
    choices = input(f"Which process id(s) should be revived {choices}: ")
    choices = choices.split(", ")
    choices = [int(c) for c in choices]

    if choices:
        for c in choices:
            multiprocessing.Process(target=serve, args=(c, )).start()

# clean control c exiting
def sigint_handler(signum, frame):
    # terminate all child processes
    for process in multiprocessing.active_children():
        process.terminate()
    # exit the main process without raising SystemExit
    try:
        sys.exit(0)
    except SystemExit:
        pass


if __name__ == '__main__':
    
    processes = create_processes()

    signal.signal(signal.SIGINT, sigint_handler)

    start_processes(processes)

    ## TEST kill revive
    for i in range(5):
        time.sleep(8)
        try:
            kill_revive(processes)
        except EOFError:
            sys.exit(0)

    ### TEST random commits
    # for _ in range(5):
    #     time.sleep(8)
    #     try:
    #         input("Start random commits: ")
    #         random_commits()
    #     except EOFError:
    #         sys.exit(0)
        