import sqlite3
from datetime import datetime

class Statistics():
    def __init__(self):
        self.db = sqlite3.connect("clopes.sqlite3")
        self.users = {}

    def newstate(self, entry):
        card = entry[1]
        unix = int(entry[2])

        user = self.users[card]

        if user['state'] == 'nothing':
            user['states']['nothing'] += unix - user['last']
            user['counter']['nothing'] += 1
            user['state'] = 'queue'

        else:
            if user['state'] == 'queue':
                user['states']['queue'] += unix - user['last']
                user['counter']['queue'] += 1
                user['state'] = 'outside'

            else:
                user['states']['outside'] += unix - user['last']
                user['counter']['outside'] += 1
                user['state'] = 'nothing'

        user['last'] = unix

    def stats(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT u.name, h.card, strftime('%s', h.moment, 'localtime')
            FROM users u, history h
            WHERE u.card = h.card
        """)
        entries = cur.fetchall()

        for entry in entries:
            unix = int(entry[2])
            x = datetime.utcfromtimestamp(unix)

            if entry[1] not in self.users:
                self.users[entry[1]] = {
                    'state': 'nothing',
                    'last': unix,
                    'states': {
                        'nothing': 0,
                        'queue': 0,
                        'outside': 0
                    },
                    'counter': {
                        'nothing': 0,
                        'queue': 0,
                        'outside': 0,
                    },
                    'name': entry[0]
                }

            self.newstate(entry)

    def elapsed(self, value):
        if value > 86400:
            return "%.1f heures" % (value / 3600)

        if value > 3600:
            hrs = value / 3600
            mins = (value - (int(hrs) * 3600)) / 60

            return "%d heures, %d minutes" % (hrs, mins)

        if value > 60:
            mins = value / 60
            return "%d minutes" % mins

        return "%d secondes" % value

    def dump(self):
        for uid in self.users:
            user = self.users[uid]

            print("== %s ==" % user['name'])
            print("  File d'attente   : %s" % self.elapsed(user['states']['queue']))
            print("  Sur la terrasse  : %s" % self.elapsed(user['states']['outside']))
            print("  Nombre de sorties: %s" % user['counter']['outside'])
            print("")


if __name__ == '__main__':
    s = Statistics()
    s.stats()
    s.dump()
