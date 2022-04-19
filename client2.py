
from socket import *
from getmac import get_mac_address as gma
from Message import Message, MESSAGE_TYPE

"""
Message Types
    0 = Discover
    1 = Offer
    2 = Request
    3 = Decline
    4 = Ack
    5 = Negative Ack
    6 = Release 
    7 = Informational 
"""

class Client:

    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.serverPort = 18000
        self.macAddress = 'fc:e2:6c:14:8a:f1'
        self.hostName = 'localhost'
        self.ipAddress = '0.0.0.0'
        self.lastIP = None
        self.timestamp = None
        self.loop = True

        self.messageType = None
        self.messageMac = None
        self.messageIP = None
        self.messageTimestamp = None

    # parses message from server
    def setMessageInfo(self, serverMessage):
        message = Message(None, None, None, None)
        message.message_str = serverMessage
        message.decodeMessage()
        self.messageType = message.messageType
        self.messageMac = message.clientMac
        self.messageIP = message.clientIP
        self.messageTimestamp = message.timestamp

    


    def sendDISCOVER(self):
        print (f"Client2: I am DISCOVERING with MAC address {self.macAddress}")
        # encode message
        message = Message(MESSAGE_TYPE[0], self.macAddress, self.ipAddress, self.timestamp)
        message.encodeMessage()

        # send Discover message
        self.socket.sendto(message.message_str.encode(), (self.hostName, self.serverPort))
        
        # wait for server response
        self.receiveMessage()

    def sendREQUEST(self):
        print (f"Client2: I am REQUESTING IP address {self.messageIP}")
        # encode message
        message = Message(MESSAGE_TYPE[2], self.macAddress, self.messageIP, self.messageTimestamp)
        message.encodeMessage()

        # send Request message
        self.socket.sendto(message.message_str.encode(), (self.hostName, self.serverPort))

        # wait for server response
        self.receiveMessage()

    def sendRELEASE(self):
        print (f"Client2: I want to RELEASE my IP address {self.ipAddress}")
        # encode message
        message = Message(MESSAGE_TYPE[5], self.macAddress, self.ipAddress, None)
        message.encodeMessage()

        # send Release message
        self.socket.sendto(message.message_str.encode(), (self.hostName, self.serverPort))

        # reset ip
        self.ipAddress = '0.0.0.0'

    def sendRENEW(self):
        print (f"Client2: I want to RENEW my IP address {self.lastIP}")
        # encode message
        message = Message(MESSAGE_TYPE[6], self.macAddress, self.lastIP, None)
        message.encodeMessage()

        # send Renew message
        self.socket.sendto(message.message_str.encode(), (self.hostName, self.serverPort))

        # wait for server response
        self.receiveMessage()

    def quit(self):
        self.socket.close()
        self.loop = False

    def checkMessageMacMatches(self):
        if self.messageMac == self.macAddress: 
            return True 
    
    def checkTimestampExpired(self):
        if self.messageTimestamp == 0:
            return True

    # client receives OFFER
    def recOFFER(self, serverMessage):
        # load message data
        self.setMessageInfo(serverMessage)
        # feedback
        print (f"Client2: I have received an OFFER for {self.messageIP}")

        # check if Mac matches our Mac address
        if self.checkMessageMacMatches() and not self.checkTimestampExpired():
            self.sendREQUEST()
        else:
            self.quit()

        # when receives an OFFER, check if MAC address is same as OURS
            # if yes
                # check if timestamp expired
                    # if not expired, send a REQUEST w/ MAC, IP, timestamp ??????
            # if not
                # send REQUEST
                    # if DECLINEd, print message saying request declined and terminate

    # client receives ACKNOWLEDGE
    def recACKNOWLEDGE(self, serverMessage):
        # load message data
        self.setMessageInfo(serverMessage)
        # feedback
        print (f"Client2: I have received ACKNOWLEDGEMENT that IP address {self.messageIP} belongs my MAC address {self.messageMac}")

        if self.checkMessageMacMatches():
            print (f"Client2: IP address {self.messageIP} has been assigned to this client, which will be expired at time {self.messageTimestamp}.")
        else:
            print ("Client2: That is not our MAC address, terminating.")
            self.quit()
        # when receives an ACKNOWLEDGE, check if MAC address is same as OURS
            # if not, print a proper message & terminate
            # else print IP address "x.x.x.x" has been assigned to this client, which will be expired at time TTT.

        # change IP Address
        self.ipAddress = self.messageIP
        self.lastIP = self.ipAddress

    # client receives DECLINE
    def recDECLINE(self):
        print ("Client2: Our request was DECLINED, terminating.")
        self.quit()


    def sendPrintList(self):
        # encode message
        message = Message(MESSAGE_TYPE[7], self.macAddress, self.messageIP, self.messageTimestamp)
        message.encodeMessage()

        # send Request message
        self.socket.sendto(message.message_str.encode(), (self.hostName, self.serverPort))
    
    def printMenu(self):
        menu = {'1': "Release", '2': "Renew", '3': "Exit & Quit"}
        options = menu.keys()
        for selection in options:
            print (selection, menu[selection])
        selection = input("Enter a Number:")
        if selection == '1':
            client.sendRELEASE()
        elif selection == '2':
            client.sendRENEW()
        elif selection == '3':
            client.quit()

    def receiveMessage(self):
        message, serverAddress = client.socket.recvfrom(2048)
        message = message.decode()

        # when receives an OFFER
        if 'Offer' in message:
            client.recOFFER(message)
        # when receives an ACK
        if 'Ack' in message:
            client.recACKNOWLEDGE(message)
        # when receives a DECLINE
        if 'Decline' in message:
            client.recDECLINE()


if __name__ == "__main__":
    client = Client()
    client.sendDISCOVER()

    while client.loop is True:
        client.printMenu()








   
