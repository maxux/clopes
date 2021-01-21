# Fumer des clopes sur la terrace

La terrace est limitée à 2 personnes à la fois.

Pour savoir qui peut y aller et dans quel ordre, un système de carte rfid est mis devant la porte.

Chaque utilisateur a une carte:
- Il badge une première fois pour se mettre dans la file d'attente
- Il badge une seconde fois une fois qu'il sort, pour aller sur la terrace
- Il badge une troisième fois une fois qu'il revient, pour libérer la place

Ce dépôt contient le code de l'interface web qui affiche la file d'attente et les utilisateurs
sur la terrace. Il contient également le code qui maintient une base de donnée pour les utilisateurs
et un historique.

# Technique

Un capteur rfid sur un Raspberry Pi attend une carte, une fois qu'une carte est à portée, il envoit
l'identifiant de la carte dans un channel redis.

Le script `dispatch.py` attend sur le channel redis, une carte, une fois qu'une carte est reçue, il
vérifie dans quel file opérer et met à jour les files. La mise à jour est envoyée via websockets
aux clients web.

![Preview](https://i.imgur.com/OxGFg58.png)
