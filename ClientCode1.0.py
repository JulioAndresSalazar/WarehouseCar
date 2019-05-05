import socket

# Enter IP address of the pi you are talking to, e.g. 10.245.150.164
IP_address = '10.245.158.79' 
PORT_num = 2460 
BUFFER = 1024

def sendData(msg):
    # connect to server, send message, get back response
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # set up socket
    s.connect((IP_address, PORT_num))
    s.sendall(message) # send message
    data = s.recv(BUFFER) # get back response
    s.close() # tells the server that the connection is done
    
    # print what was returned by server
    print(data)

message_pre = '11N'
message = str(message_pre).encode("utf-8")
sendData(message)


