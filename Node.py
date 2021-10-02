from aiorpc import server, RPCClient
import asyncio, uvloop, json, sys, time
from datetime import datetime

DB_FILE = "data/bank.db.json"

class Node:

    async def rpc_requestCSXN(self, requester, timestamp):
        self.log(requester + " is requesting the CSXN")
        if self.requestTimestamp == None or (self.requestTimestamp, self.my_port) > (timestamp, requester):
            self.log("Granted request to " + requester)
            return True
        else:
            self.log("Deferring requester " + requester)
            self.deferrals.add(requester)
            return False
    
    async def __acquireCSXN(self, timestamp):
        self.requestTimestamp = timestamp
        self.responseSet = set({})
        self.log("Requesting critical section")
        for neighbor in self.neighbor_ports:
            self.log("Requesting CSXN from " + neighbor)
            ret = await RPCClient('127.0.0.1', int(neighbor)).call('rpc_requestCSXN', self.my_port, self.requestTimestamp)
            if ret: # we haven't been deferred - yay!
                self.responseSet.add(neighbor)
        while self.responseSet != self.neighbor_ports:
            await asyncio.sleep(1) # Probably not the right way to do this
        self.log("Acquired CSXN")

    async def acquireCSXN(self, timestamp):
        await asyncio.Task(self.__acquireCSXN(timestamp))
        

    async def __releaseCSXN(self):
        self.requestTimestamp = None
        for neighbor in self.deferrals:
            self.log("Releasing the CSXN to " + neighbor)
            await RPCClient('127.0.0.1', int(neighbor)).call('rpc_csxnIsReleased', self.my_port)
    
    async def releaseCSXN(self):
        self.log("Releasing CSXN")
        asyncio.get_event_loop().create_task(self.__releaseCSXN())

    async def rpc_csxnIsReleased(self, requester):
        self.log(requester + " has released the critical section")
        self.responseSet.add(requester)
    
    async def rpc_depositCash(self, timestamp, account, amount):
        await self.acquireCSXN(timestamp)
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            data[account] += amount
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        await self.releaseCSXN()

    async def rpc_withdrawCash(self, timestamp, account, amount):
        await self.acquireCSXN(timestamp)
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            data[account] -= amount
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        await self.releaseCSXN()

    async def rpc_applyInterest(self, timestamp, account, rate):
        await self.acquireCSXN(timestamp)
        self.log(("Applying %0.2f%% interest to account %s") % (rate * 100, account))
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            data[account] *= (1 + rate) # This is an actual problem in banking and not the way at all to solve it :-)
        with open(DB_FILE, "w") as file:
            json.dump(data, file)
        await self.releaseCSXN()
    
    async def rpc_checkBalance(self, timestamp, account):
        await self.acquireCSXN(timestamp)
        with open(DB_FILE, "r") as file:
            data = json.load(file)
            toReturn = data[account]
        await self.releaseCSXN()
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
    
    def log(self, msg):
        print(("[%s]::[%s] %s") % (datetime.now(), self.my_port, msg))


if __name__ == '__main__':
    asyncio.run(Node(sys.argv[1], sys.argv[2:]))