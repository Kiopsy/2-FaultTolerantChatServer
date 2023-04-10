# Replication Design Exercise

## Installation
Clone the repository
```bash
git clone https://github.com/Kiopsy/Replication.git
```

## Setting up Servers and Clients

In helpers.py, make sure to set the IP/HOST of each respective server before starting.

For example, servers with IDs = 0, 1, 2 have the respective IP's:
```bash
SERVER_IPS = {50050: "10.250.78.119", 50051: "10.250.174.43", 50052: "10.250.78.119"}
```

To run the servers, splitting the server between different machines/terminals, you can run (where id = 0, 1, or 2).
```bash
python server.py id
```
Or to run all servers in the same terminal using multiprocessing, you can run:
```bash
python server.py
```

Then, run the corresponding client:
```bash
python client.py
```
and a GUI will pop up. Follow the steps there accordingly. 
If multiple clients want to connect, repeat the above step in another terminal (make sure the IPs are stated accordingly in the helpers.py file).

## Navigating the Chat App
Ensure to login/register for an account (where duplicate accounts cannot exist). When you proceed to the homepage, you can send messages to other users who have created an account. If a user exists, but is not showing up on the dropdown, make sure to reset options to query the database from the server again. 

## Fault Tolerance
To test fault-tolerance, you can shut down the servers by pressing ctrl-c if they are running in separate terminals. The server with the lowest ID will be chosen as the leader using the Bully Algorithm. In case you are using multiprocessing, you can test fault-tolerance by removing the comment from the "TEST kill revive" section in server.py. This will enable you to enter the server you want to shut down as input, and it will restart after a few seconds. Our application allows servers to rejoin, and they will automatically reconnect with each other, which might trigger another round of leader election.

## Running Unit Tests
For running unit testts,s open up a terminal and nagivate to the 
directory containing server.py and client.py. Start the servers by typing
```bash
python unit_tests.py
```
This will run all unit tests, and will print success/error for each test upon completion.
