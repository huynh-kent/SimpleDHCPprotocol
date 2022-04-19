from Message import Message, MESSAGE_TYPE
from socket import *

class Admin:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.hostName = 'localhost'
        self.serverPort = 18000
        self.list = None
        

    def sendPrintList(self):
        # encode message
        message = Message(MESSAGE_TYPE[7], None, None, None)
        message.encodeMessage()

        # send Request message
        self.socket.sendto(message.message_str.encode(), (self.hostName, self.serverPort))
        serverMessage, serverAddress = self.socket.recvfrom(2048)

        # receive list from server
        newmessage = Message(None, None, None, None)
        newmessage.message_str = serverMessage.decode()
        newmessage.decodeMessage()

        # clean up list from message and print
        self.list = newmessage.clientIP
        listrecord = self.list.split('), (')
        chars_to_remove = { '(': '',
                    ')': '',
                    '[': '',
                    ']': '',                        
                    }
        for record in listrecord:
            for key, value in chars_to_remove.items():
                record = record.replace(key, value)
            print (record)

if __name__ == "__main__":
    admin = Admin()
    # send server list message
    admin.sendPrintList()
