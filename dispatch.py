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

    def resolv(self, card):
        cur = self.db.cursor()
        cur.execute("SELECT name FROM users WHERE card = ?", (card,))
        x = cur.fetchall()

        if len(x) > 0:
            return x[0][0]

        return "Unknown (%s)" % card

    def persist(self, card):
        cur = self.db.cursor()
        cur.execute("INSERT INTO history (card, moment) VALUES (?, datetime());", (card,))
        self.db.commit()

    def getlist(self):
        outside = []
        queue = []

        for item in self.redis.lrange("clope-outside", 0, 100):
            outside.append(self.resolv(item.decode('utf-8')))

        for item in self.redis.lrange("clope-queue", 0, 100):
            queue.append(self.resolv(item.decode('utf-8')))

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

    def process(self, card):
        who = self.resolv(card)

        print("[+] card scanned: %s [%s]" % (card, who))

        if self.redis.execute_command("lpos", "clope-outside", card) is not None:
            print("[+] queue: removing from outside: %s" % card)
            self.redis.lrem("clope-outside", 1, card)

        else:
            if self.redis.execute_command("lpos", "clope-queue", card) is not None:
                print("[+] queue: moving outside: %s" % card)
                self.redis.rpush("clope-outside", card)
                self.redis.lrem("clope-queue", 1, card)

            else:
                print("[+] queue: adding to queue: %s" % card)
                self.redis.rpush("clope-queue", card)

        self.persist(card)

    async def redisloop(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe("rfid-card")

        while True:
            message = pubsub.get_message()

            if message and message['type'] == 'message':
                card = message['data'].decode('utf-8')
                self.process(card)

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

