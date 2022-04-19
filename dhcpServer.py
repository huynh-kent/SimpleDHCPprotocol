from random import random
from socket import *

from numpy import record

from Message import Message, MESSAGE_TYPE
from random import randint
import sqlite3
import time

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


class Server:

    def __init__(self):
        # create server socket
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.port = 18000
        self.socket.bind(('', self.port))

        self.clientMac = None
        self.clientIP = None
        self.clientIndex = None

        self.hostName = None
        self.leaseTime = 60 # seconds
        self.recordNumber = 1

        self.t = time.localtime()
        self.current_time = time.strftime("%H:%M:%S", self.t)

        # connection with database using sqlite
        self.con = sqlite3.connect(':memory:')
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS ipList
                        (ip text, mac text, timestamp int, acked boolean, record int)''')

        for i in range(14):
            self.cur.execute(f"INSERT INTO ipList VALUES ('192.168.45.{i+1}', 'N/A', 0, False, 0)")

        #self.con.commit()
    def timestampTime(self):
        return time.ctime(time.time()+self.leaseTime)

    def sendOFFER(self):
        print (f"Server: Assigning IP {self.clientIndex[0]} to MAC Address {self.clientMac}")
        # encode message with info
        message = Message(MESSAGE_TYPE[1], self.clientMac, self.clientIndex[0], self.timestampTime())
        message.encodeMessage()

        # send Offer message
        self.socket.sendto(message.message_str.encode(), clientAddress)

    def sendACK(self):
        print (f"Server: Acknowledging IP {self.clientIndex[0]} with MAC Address {self.clientMac}")
        # encode message with info
        message = Message(MESSAGE_TYPE[3], self.clientMac, self.clientIndex[0], self.timestampTime())
        message.encodeMessage()

        # send Acknowledge message
        self.socket.sendto(message.message_str.encode(), clientAddress)

    def sendDECLINE(self):
        print (f"Server: I am declining the request from {self.clientMac}.")
        # encode message 
        message = Message(MESSAGE_TYPE[4, self.clientMac, None, None])
        message.encodeMessage()

        # send Decline message
        self.socket.sendto(message.message_str.encode(), clientAddress)

    def setAckedTrue(self):
        with self.con:
            self.cur.execute(f"UPDATE ipList SET acked = True where ip = '{self.clientIndex[0]}'")

    def setAckedFalse(self):
        with self.con:
            self.cur.execute(f"UPDATE ipList SET acked = False WHERE ip = '{self.clientIndex[0]}'")

    def assignIP(self):
        with self.con:
            self.cur.execute(f"UPDATE ipList SET mac = '{self.clientMac}' WHERE ip = '{self.clientIndex[0]}'")

        self.updateTimestamp()

    
    def printList(self):
        # create recordlist to send to admin
        record_list = list(self.cur.execute('SELECT * FROM ipList'))
        print ("Server: Sending Record List to Admin")
        # encode message with info
        message = Message(MESSAGE_TYPE[3], None, record_list, None)
        message.encodeMessage()

        # send RecordList message
        self.socket.sendto(message.message_str.encode(), clientAddress)




    def checkMacInList(self):
        for row in self.cur.execute(f"SELECT * FROM ipList where mac = '{self.clientMac}' LIMIT 1"):
            index = row
        try:
            self.clientIndex = index
            print (f"Server: I see MAC {self.clientMac} is in our record.")
            return True
        except:
            print (f"Server: I see MAC {self.clientMac} is not in record.")

    def checkAvailableIP(self):
        for row in self.cur.execute("SELECT * FROM ipList where mac = 'N/A' or timestamp = 0 LIMIT 1"):
            index = row
        try:
            self.clientIndex = index
            #print (f"Available IP - {self.clientIndex[0]}")
            return True
        except:
            print ("Server: No Available IP Address")
        

    def checkTimestampExpired(self):
        if time.ctime() > self.clientIndex[2] or self.clientIndex == 0:
            print ("Server: Timestamp has expired")
            return True


    def checkMessageIPMatches(self):
        for row in self.cur.execute(f"SELECT * FROM ipList where mac = '{self.clientMac}' and ip = '{self.clientIP}'"):
            index = row
        try:
            self.clientIndex = index
            #print (self.clientIndex)
            return True
        except:
            print ("Server: IP Doesnt Match")

    def releaseIP(self):
        self.setTimestampCurrentTime()
        # 
        # with self.con:
        #    self.cur.execute(f"UPDATE ipList SET mac = 'N/A' WHERE ip = '{self.clientIndex[0]}'")

    def setTimestampCurrentTime(self):
        with self.con:
            self.cur.execute(f"UPDATE ipList SET timestamp = '{self.current_time}' WHERE ip = '{self.clientIndex[0]}'")

    def updateTimestamp(self):
        with self.con:
            self.cur.execute(f"UPDATE ipList SET timestamp = '{self.timestampTime()}' WHERE ip = '{self.clientIndex[0]}'")
        self.updateRecord()

    def updateRecord(self):
        with self.con:
            self.cur.execute(f"UPDATE ipList SET record = '{self.recordNumber}' WHERE ip = '{self.clientIndex[0]}'")
        self.recordNumber += 1

    def setClientInfo(self, clientMessage):
        message = Message(None, None, None, None)
        message.message_str = clientMessage
        message.decodeMessage()

        self.clientMac = message.clientMac
        self.clientIP = message.clientIP

    def recDISCOVER(self, clientMessage):
        # check clients info
        self.setClientInfo(clientMessage)
        # print feedback
        print (f"Server: I see that client with MAC address {self.clientMac} is DISCOVERING.")

        # check if mac address exists in list
        if self.checkMacInList():
            if self.checkTimestampExpired():
                self.updateTimestamp()
                self.sendOFFER()
            else:
                self.sendACK()
                # send ACKNOWLEDGE w/ client mac, ip, and timestamp
        elif self.checkAvailableIP():
            self.assignIP()
            self.setAckedFalse()
            self.sendOFFER()
        else: # no available IP 
            self.sendDECLINE()
    
    def recREQUEST(self, clientMessage):
        # check clients info
        self.setClientInfo(clientMessage)
        # print feedback
        print (f"Server: I see that client with MAC address {self.clientMac} is REQUESTING IP {self.clientIP}")

        # check if IP matches assigned IP
        if self.checkMessageIPMatches() and self.checkTimestampExpired() or not self.checkMessageIPMatches():
            self.sendDECLINE()
        else: # timestamp not expired
            self.setAckedTrue()
            self.sendACK()

    # when receives a REQUEST
        # check confirm IP address matches the assigned
            # if dont match DECLINE
            # else check timestamp if expired
                # if yes DECLINE
                # else set Acked to True and send ACK message w/ MAC, IP, timestamp

    def printNewList(self):
        print ("Printing updated list of clients.")
        for row in list(self.cur.execute('SELECT * FROM ipList')):
            print (row)

    def recRELEASE(self, clientMessage):
        # check clients info
        self.setClientInfo(clientMessage)
        # print feedback

        if self.checkMacInList() and self.checkMessageIPMatches():
            self.releaseIP()
            self.setTimestampCurrentTime()
            self.setAckedFalse()
            print (f"Server: I am RELEASING MAC address {self.clientMac} from their IP {self.clientIP}.")
            self.printNewList()
        # when receives a RELEASE
            # check if MAC in list, if yes
                # release IP address
                # set timestamp to current time
                # set Acked to False
            # if not
                # do nothing

    def recRENEW(self, clientMessage):
        # check client info
        self.setClientInfo(clientMessage)
        # print feedback
        print (f"Server: I see that client with MAC address {self.clientMac} wants to RENEW their IP {self.clientIP}.")

        if self.checkMacInList():
            self.updateTimestamp()
            self.setAckedTrue()
            self.sendACK()
        elif self.checkAvailableIP():
            self.assignIP()
            self.setAckedFalse()
            self.sendOFFER()
        else:
            self.sendDECLINE()
        # when receives a RENEW message
            # check if MAC in list
                # if yes
                    # set timestamp to 60
                    # set Acked to True
                    # send ACKNOWLEDGE message w/ MAC, IP, timestamp
                # if no
                    # check if available IP
                        # if yes
                            # assign
                        # if no
                            # check timestamps
                                # if yes
                                    # assign to new client
                                    # update list & timestamp
                                    # set Acked to False
                                    # send OFFER message
                                # else 
                                    # send DECLINE message
                

if __name__ == "__main__":
    # init server
    server = Server()

    # new server records
    print ('Server Online---------------')
    #server.printList()

    while True:
        # receive messages using UDP
        message, clientAddress = server.socket.recvfrom(2048)
        message = message.decode()

        # when receives a DISCOVER
        if 'Discover' in message:
            server.recDISCOVER(message)

        # when receives a REQUEST
        if 'Request' in message:
            server.recREQUEST(message)

        # when receives a RELEASE
        if 'Release' in message:
            server.recRELEASE(message)
        
        # when receives a RENEW
        if 'Renew' in message:
            server.recRENEW(message)

        # when receives a LIST
        if 'List' in message:
            server.printList()


