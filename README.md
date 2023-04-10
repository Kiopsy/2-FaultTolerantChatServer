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

To run the servers, you can run (where id = 0, 1, or 2)
```bash
python server.py id
```
To split the server between different machines/terminals Or you can run
```bash
python server.py
```
to run all three servers using multiprocesing.

Then, run the corresponding client:
```bash
python client.py
```
and a GUI will pop up. Follow the steps there accordingly. 
If multiple clients want to connect, repeat the above step in another terminal.

## Navigating the Chat App
Ensure to login/register for an account (where duplicate accounts cannot exist). When you proceed to the homepage, you can send messages to other users who have created an account. If a user exists, but is not showing up on the dropdown, make sure to reset options to query the database from the server again. 


## Running Unit Tests
For running unit testts,s open up a terminal and nagivate to the 
directory containing server.py and client.py. Start the servers by typing
```bash
python server.py 12350
```
as the unit tests were written with the server ports being 12345, 12346, and 12347.

Now, open up another terminal and nagivate to the same directory and type
```bash
python -m unittest client.py
```
This will run all unit tests, testing individual functions of client.py and making
sure that messages are sent correctly from client to server to client.
