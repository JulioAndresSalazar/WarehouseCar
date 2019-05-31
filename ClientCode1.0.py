#This script sends data to server pi from a client Pi and waits for a reply.
import socket
IP_address = '10.245.158.79' #Enter the IP Address of the client Pi
PORT_num = 2460 
BUFFER = 1024

def sendData(msg):
    #Connect to server, send message, get back response
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((IP_address, PORT_num))
    s.sendall(message)
    data = s.recv(BUFFER)
    s.close() 
    print(data)

message_pre = '11N'
message = str(message_pre).encode("utf-8")
sendData(message)


