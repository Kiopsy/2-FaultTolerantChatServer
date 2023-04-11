import unittest
from machine import Machine
from concurrent import futures
import grpc, time, chat_service_pb2_grpc, chat_service_pb2, threading, multiprocessing

def serve(machine, server):
    chat_service_pb2_grpc.add_ChatServiceServicer_to_server(machine, server)
    server.add_insecure_port(machine.HOST + ':' + str(machine.PORT))
    server.start()

    time.sleep(1)
    machine.connect()
    machine.heartbeat_thread.start()
    server.wait_for_termination()

class TestMachine(unittest.TestCase):

    def testInitialization(self) -> None:
        # Create machines and test their port settings and IDs
        machine1 = Machine(0, True)
        machine2 = Machine(1, True)
        machine3 = Machine(2, True)

        self.assertEqual(machine1.MACHINE_ID, 0)
        self.assertEqual(machine1.PORT, 50050)
        self.assertEqual(list(machine1.PEER_PORTS.keys()), [50051, 50052])
        self.assertEqual(machine2.MACHINE_ID, 1)
        self.assertEqual(machine2.PORT, 50051)
        self.assertEqual(list(machine2.PEER_PORTS.keys()), [50050, 50052])
        self.assertEqual(machine3.MACHINE_ID, 2)
        self.assertEqual(machine3.PORT, 50052)
        self.assertEqual(list(machine3.PEER_PORTS.keys()), [50050, 50051])

        print("testInitialization passed")

    def testConnection(self) -> None:
        # Create all machines & servers
        servers = [grpc.server(futures.ThreadPoolExecutor(max_workers=10)) for _ in range(3)]
        machines = [Machine(i, True) for i in range(3)]

        # Start the each in their own thread
        threads = [threading.Thread(target = serve, args=(machines[i], servers[i])) for i in range(3)]
        for t in threads:
            t.start()

        # Sleep to give time for machines to connect
        time.sleep(3)

        # Ensure all machines are connected and have selected 50050 as a leader
        for m in machines:
            self.assertTrue(m.connected)
            self.assertTrue(all(m.peer_alive.values()))
            self.assertEqual(m.primary_port, 50050)

        # Stop machines and servers before closing
        for s, m in zip(servers, machines):
            s.stop(grace=1)
            m.stop_event.set()

        for t in threads:
            t.join()

        print("testConnection passed.")

    def testReconnect(self) -> None:
        # Create all machines & servers
        servers = [grpc.server(futures.ThreadPoolExecutor(max_workers=10)) for _ in range(3)]
        machines = [Machine(i, True) for i in range(3)]

        # Start the each in their own thread
        threads = [threading.Thread(target = serve, args=(machines[i], servers[i])) for i in range(3)]
        for t in threads:
            t.start()

        # Sleep to give time for machines to connect
        time.sleep(4)

        # Ensure all machines are connected and have selected 50050 as a leader
        for m in machines:
            self.assertTrue(m.connected)
            self.assertTrue(all(m.peer_alive.values()))
            self.assertEqual(m.primary_port, 50050)

        # Disconnect the leader machine & server
        machines[0].stop_machine()
        servers[0].stop(grace=1)
        
        # Give time for machines to re-elect
        time.sleep(4)

        # Ensure that other machines reelect a leader
        for m in machines[-2:]:
            self.assertEquals(m.primary_port, 50051)

        # Stop machines and servers before closing
        for s, m in zip(servers, machines):
            s.stop(grace=1)
            m.stop_event.set()

        for t in threads:
            t.join()

        print("testReconnect passed")

if __name__ == '__main__':
    print("Begining unit tests...")
    unittest.main()
