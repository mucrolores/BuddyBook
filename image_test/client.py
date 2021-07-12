import socket
import pickle

import base64

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect(('localhost',8888))


#msg = "Client Test"
#clientSocket.send(msg.encode("UTF-8"))
file_name = "test_image.jpg"

with open(file_name, "rb")as fp:
    img = fp.read()
    
msg =  {"message":"Client Test", "test":("tets",), "test1":img}

clientSocket.send(pickle.dumps(msg))


data = clientSocket.recv(1024)
print(data.decode())
clientSocket.close()
print("closed")