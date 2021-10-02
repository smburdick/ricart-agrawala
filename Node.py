from aiorpc import server, RPCClient
import asyncio, uvloop, json, sys
from datetime import datetime

DB_FILE = "bank.db.json"

class Node:

    def log(self, msg):
        print(("[%s]::[%s] %s") % (datetime.now(), self.my_port, msg))

    def rpc_requestCSXN(self, requester, timestamp):
        self.log(requester + " is requesting the CSXN")
        if self.requestTimestamp == None or (self.my_port, self.requestTimestamp) > (requester, timestamp):
            return True
        else:
            self.deferrals.add(requester)
            return False

    async def __acquireCSXN(self, neighbor): # Ask neighbor for the critical section
        ret = await RPCClient('127.0.0.1', int(neighbor)).call('rpc_requestCSXN', self.my_port, self.requestTimestamp)
        if ret: # we haven't been deferred
            self.responseSet.add(neighbor)
    
    def acquireCSXN(self, timestamp):
        self.requestTimestamp = timestamp
        self.responseSet = set({})
        for neighbor in self.neighbor_ports:
            self.log("Requesting CSXN from " + neighbor)
            asyncio.create_task(self.__acquireCSXN(neighbor))
        while self.responseSet != self.neighbor_ports:
            pass


    async def __releaseCSNXN(self, neighbor):
        await RPCClient('127.0.0.1', int(neighbor)).call('rpc_csxnIsReleased', self.my_port)

    def releaseCSXN(self):
        self.requestTimestamp = None
        #loop = asyncio.get_event_loop()
        for neighbor in self.deferrals:
            asyncio.create_task(self.__releaseCSNXN(neighbor))

    async def rpc_csxnIsReleased(self, requester):
        self.responseSet.add(requester)
    
    async def rpc_depositCash(self, timestamp, account, amount):
        self.acquireCSXN(timestamp)
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            data[account] += amount
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        self.releaseCSXN()

    async def rpc_withdrawCash(self, timestamp, account, amount):
        self.acquireCSXN(timestamp)
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            data[account] -= amount
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        self.releaseCSXN()

    async def rpc_applyInterest(self, timestamp, account, rate):
        self.acquireCSXN(timestamp)
        self.log(("Applying %0.2f%% interest to account %s") % (rate * 100, account))
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            data[account] *= (1 + rate)
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        self.releaseCSXN()
    
    async def rpc_checkBalance(self, timestamp, account):
        self.acquireCSXN(timestamp)
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            toReturn = data[account]
        self.releaseCSXN()
        return toReturn

    def __init__(self, port, neighbor_ports):
        self.requestTimestamp = None
        self.neighbor_ports = set(neighbor_ports)
        self.my_port = port
        #self.vc = {p : 0 for p in neighbor_ports + [port]}
        self.deferrals = set({}) # Processes I have deferred
        self.responseSet = set({}) # Processes I have gotten a response from to access CSXN
        self.requestTimestamp = None
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        server.register("rpc_requestCSXN", self.rpc_requestCSXN)
        server.register("rpc_csxnIsReleased", self.rpc_csxnIsReleased)
        server.register("rpc_depositCash", self.rpc_depositCash)
        server.register("rpc_withdrawCash", self.rpc_withdrawCash)
        server.register("rpc_applyInterest", self.rpc_applyInterest)
        server.register("rpc_checkBalance", self.rpc_checkBalance)
        coro = asyncio.start_server(server.serve, '127.0.0.1', int(port), loop=loop)
        s = loop.run_until_complete(coro)
        self.log("Listening")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            s.close()
            loop.run_until_complete(s.wait_closed())

if __name__ == '__main__':
    Node(sys.argv[1], sys.argv[2:])