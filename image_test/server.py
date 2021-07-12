import socket
import pickle
import sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 8888
s.bind(('localhost', port))

s.listen(5)

while True:
    try:
        conn, address = s.accept()
    except KeyboardInterrupt:
        sys.exit(0)
    print("Address: ", address)
    data = []
    count = 0
    while True:
        try:
            packet = conn.recv(1024)
            if not packet:
                break
            else:
                try:
                    data.append(packet)
                    if len(packet) < 1024:
                        data = pickle.loads(b"".join(data))
                        with open("test.JPEG", "wb") as fp:
                            fp.write(data["test1"])
                        print("finish")
                        break
                except pickle.UnpicklingError:
                    print("error")
                    pass

        except ConnectionAbortedError:
            break
    msg = "Success"

    conn.send(msg.encode('UTF-8'))
    conn.close()
    print("closed")
