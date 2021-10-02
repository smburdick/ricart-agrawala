from aiorpc import RPCClient

import asyncio, uvloop, json

async def do(p1, p2, p3):
    await p1.call('rpc_applyInterest', 2, 'B', .10)
    

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
p1 = RPCClient('127.0.0.1', 6000)
p2 = RPCClient('127.0.0.1', 6001)
p3 = RPCClient('127.0.0.1', 6002)
with open("bank.db.json", "w") as file:
    dict = {}
    accounts = ['A', 'B', 'C']
    for k in accounts:
        dict[k] = 100
    json.dump(dict, file)

loop.run_until_complete(do(p1, p2, p3))
for p in [p1, p2, p3]:
    p.close()