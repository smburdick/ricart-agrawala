from aiorpc import server
import asyncio
import uvloop


def echo(msg):
    return msg

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
server.register("echo", echo)
coro = asyncio.start_server(server.serve, '127.0.0.1', 6000, loop=loop)
s = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    s.close()
    s.run_until_complete(s.wait_closed())