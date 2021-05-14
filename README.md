IA pour le jeu Abalone
Communique avec un serveur de tournoi:
https://github.com/qlurkin/PI2CChampionshipRunner



Crée par Eliott Nys (195193) & Matthis Brenez (195003)



Pour lancer le client (sur un port au choix) tapez la commande suivante dans un terminal:
```shell
python client.py <port>
```


Bibliothèques:
Tous les modules utilisés sont tirés de la librairie standard de python.
(modules: sys, json, socket, random et copy)


Stratégie:
Cette IA utilise un algorithme de type negamax avec pruning et profondeur limitée à 2.
Pour l'heuristique des noeuds, on calcul un score en fonction des positions occupées sur le plateau. (voir variable posValues dans IA.py ligne 31)
Au plus un pion est proche du centre, au plus il rapporte de points. La distribution n'est pas linéaire: au plus on s'approche du bord du plateau de jeu, au plus les écarts de points deviennent importants. Le score d'un joueur pour un état donné correspond à la différence de points entre le joueur et son adversaire.