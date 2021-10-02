import asyncio, json, aiorpc

async def apply_interest(p, time, acct, rate):
    await p.call('rpc_applyInterest', time, acct, rate)

async def deposit_cash(p, time, acct, amt):
    await p.call('rpc_depositCash', time, acct, amt)

async def withdraw_cash(p, time, acct, amt):
    await p.call('rpc_withdrawCash', time, acct, amt)

async def check_balance(p, time, acct):
    balance = await p.call('rpc.checkBalance', time, acct)
    print(("%s : $%d") % (acct, balance))

async def main():
    p1 = aiorpc.RPCClient('127.0.0.1', 6000)
    p2 = aiorpc.RPCClient('127.0.0.1', 6001)
    p3 = aiorpc.RPCClient('127.0.0.1', 6002)
    # Only run this if nobody else is accessing the file!
    with open("data/bank.db.json", "w") as file:
        dict = {}
        accounts = ['A', 'B', 'C']
        for k in accounts:
            dict[k] = 100
        json.dump(dict, file)

    await asyncio.gather(
        apply_interest(p3, 2, 'B', .10)
        , deposit_cash(p1, 4, 'A', 20)
        , withdraw_cash(p2, 4, 'C', 30)
        , apply_interest(p1, 57, 'C', .10)
        
    )

    for p in [p1, p2, p3]:
        p.close()
    
if __name__ == '__main__':
    asyncio.run(main())