import asyncio
import websockets
import json
import redis
import time
import sqlite3

class Dispatcher():
    def __init__(self):
        self.wsclients = set()
        self.payloads = {}
        self.redis = redis.Redis("10.241.0.240")
        self.db = sqlite3.connect("clopes.sqlite3")

        self.outside = []
        self.queue = []

    def resolv(self, card):
        cur = self.db.cursor()
        cur.execute("SELECT name FROM users WHERE card = ?", (card,))
        x = cur.fetchall()

        if len(x) > 0:
            return x[0][0]

        return "Unknown (%s)" % card

    def getlist(self):
        outside = []
        queue = []

        for i in self.outside:
            outside.append(self.resolv(i))

        for i in self.queue:
            queue.append(self.resolv(i))

        return {"queue": queue, "outside": outside}

    #
    # Websocket
    #
    async def wsbroadcast(self, type, payload):
        if not len(self.wsclients):
            return

        goodcontent = json.dumps({"type": type, "payload": payload})

        for client in list(self.wsclients):
            if not client.open:
                continue

            content = goodcontent

            try:
                await client.send(content)

            except Exception as e:
                print(e)

    async def wspayload(self, websocket, type, payload):
        content = json.dumps({"type": type, "payload": payload})
        await websocket.send(content)

    async def handler(self, websocket, path):
        self.wsclients.add(websocket)

        print("[+] websocket: client connected")

        try:
            await self.wspayload(websocket, "update", self.getlist())

            while True:
                if not websocket.open:
                    break

                await asyncio.sleep(1)

        finally:
            print("[+] websocket: client disconnected")
            self.wsclients.remove(websocket)

    async def redisloop(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe("rfid-card")

        while True:
            message = pubsub.get_message()

            if message and message['type'] == 'message':
                card = message['data'].decode('utf-8')
                who = self.resolv(card)

                print("[+] card scanned: %s [%s]" % (card, who))

                if card in self.outside:
                    print("[+] queue: removing from outside: %s" % card)
                    self.outside.remove(card)

                else:
                    if card in self.queue:
                        print("[+] queue: moving outside: %s" % card)
                        self.outside.append(card)
                        self.queue.remove(card)

                    else:
                        print("[+] queue: adding to queue: %s" % card)
                        self.queue.append(card)

                print("[+] forwarding data to clients")

                # forwarding
                await self.wsbroadcast("update", self.getlist())

            await asyncio.sleep(0.1)

    def run(self):
        # standard polling handlers
        loop = asyncio.get_event_loop()
        loop.set_debug(True)

        # handle websocket communication
        websocketd = websockets.serve(self.handler, "0.0.0.0", "2010")
        asyncio.ensure_future(websocketd, loop=loop)
        asyncio.ensure_future(self.redisloop(), loop=loop)

        print("[+] waiting for clients or slaves")
        loop.run_forever()

if __name__ == '__main__':
    dashboard = Dispatcher()
    dashboard.run()

