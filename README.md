# Jean-Loup 🪴

> [!NOTE]
> Il s'agit ici de la branche `reboot` qui a terme remplacera totalement la branche `main`.


## Structure du projet

Le project est structuré avec la convention suivante :
* Dans [./sources](./sources/) va se trouver l'ensemble du code (majoritairement en Python nécessaire au logiciel)
* Dans [./packages](./packages/) va se trouver tout ce qui est nécessaire pour builder les packages Arch Linux que l'on va utiliser, à savoir :
    * Le logiciel `jean-loup`
    * Et aussi ses dépendences (pour faire marcher la caméra sur le Raspberry Pi Zero 2 W)
* Dans [./system](./system/) va se trouver tout ce qui est nécessaire pour builder l'image d'Arch Linux pré-configurée que l'on va écrire sur la carte SD


