import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import socket
import initFile
import threading
import json

global serverIP, serverPort
serverIP = ""
serverPort = ""


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Socket'
        self.left = 100
        self.top = 120
        self.width = 800
        self.height = 700

        self.ServerIPTextBox = ""
        self.ServerPortTextBox = ""
        self.ServerCreateButton = ""
        self.ClientIPTextBox = ""
        self.ClientPortTextBox = ""
        self.ChatBar = ""
        self.InputTextBox = ""
        self.SendMessageButton = ""

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Message in statusbar.')

        startX = 20
        startY = 10

        # Server setting part__________________________

        self.IPLabel = QLabel(self)
        self.IPLabel.move(startX, startY)
        self.IPLabel.setText("Server_IP")

        self.PortLabel = QLabel(self)
        self.PortLabel.move(startX + 160, startY)
        self.PortLabel.setText("Port")

        self.ServerIPTextBox = QLineEdit(self)
        self.ServerIPTextBox.move(startX, startY + 30)
        self.ServerIPTextBox.resize(150, 30)

        self.ServerPortTextBox = QLineEdit(self)
        self.ServerPortTextBox.move(startX + 160, startY + 30)
        self.ServerPortTextBox.resize(40, 30)

        self.ServerCreateButton = QPushButton("Create Server", self)
        self.ServerCreateButton.move(startX + 220, startY + 30)
        self.ServerCreateButton.clicked.connect(self.CreateServer)

        # Client setting part__________________________

        self.IPLabel = QLabel(self)
        self.IPLabel.move(startX + 350, startY)
        self.IPLabel.setText("Client_IP")

        self.PortLabel = QLabel(self)
        self.PortLabel.move(startX + 510, startY)
        self.PortLabel.setText("Port")

        self.ClientIPTextBox = QLineEdit(self)
        self.ClientIPTextBox.move(startX + 350, startY + 30)
        self.ClientIPTextBox.resize(150, 30)

        self.ClientPortTextBox = QLineEdit(self)
        self.ClientPortTextBox.move(startX + 510, startY + 30)
        self.ClientPortTextBox.resize(40, 30)

        # messagePart

        self.ChatBar = QTextEdit(self)
        self.ChatBar.setReadOnly(True)
        self.ChatBar.move(startX, startY + 70)
        self.ChatBar.resize(600, 500)

        # inputBar

        self.InputTextBox = QLineEdit(self)
        self.InputTextBox.move(startX, startY + 590)
        self.InputTextBox.resize(400, 30)

        self.SendMessageButton = QPushButton("Send", self)
        self.SendMessageButton.move(startX + 420, startY + 590)
        self.SendMessageButton.clicked.connect(self.SendMessage)

        self.show()

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.TextEdit()
        textboxValue = "test"
        print("Hello" + textboxValue)

    def CreateServer(self):
        global serverIP, serverPort
        serverIP = str(self.ServerIPTextBox.text())
        serverPort = int(str(self.ServerPortTextBox.text()))
        serverThread = threading.Thread(target=server_init)
        serverThread.start()
        LogMessage = "Server Created at IP (" + str(serverIP) + "):" + str(serverPort)
        print(LogMessage)
        self.ChatBar.append(LogMessage)

    def SendMessage(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((str(self.ClientIPTextBox.text()), int(str(self.ClientPortTextBox.text()))))
        clientSocket.send(str(self.InputTextBox.text()).encode(initFile.EncodeSet))
        toSend = "Local" + ":" + str(self.InputTextBox.text())
        self.ChatBar.append(toSend)
        clientSocket.close()

    def setMessage(self, Message):
        self.ChatBar.append(Message)


def server_init():
    global serverSocket, serverIP, serverPort

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((str(serverIP), int(serverPort)))
    serverSocket.listen(10)
    while True:
        (connection, address) = serverSocket.accept()
        global messageBuffer
        messageBuffer = connection.recv(4096).decode()
        if messageBuffer:
            print("Message From IP :", address, ", with message :", messageBuffer)
            toSend = str(address) + ":" + str(messageBuffer)
            ex.setMessage(toSend)
        connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
