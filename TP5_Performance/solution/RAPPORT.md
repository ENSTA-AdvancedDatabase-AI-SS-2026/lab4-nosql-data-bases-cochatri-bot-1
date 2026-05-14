# Rapport TP5 - Performance & Optimisation NoSQL

## Tableau Comparatif Décisionnel

| Critère | Redis | MongoDB | Cassandra | Neo4j |
| :--- | :--- | :--- | :--- | :--- |
| **Débit écriture** | Très Élevé (~100k-500k ops/s) | Élevé (avec BulkWrite, ~50k-100k) | Très Élevé (Multi-nœuds, écritures distribuées) | Moyen (Complexité transactionnelle ACID) |
| **Débit lecture** | Exceptionnel (< 1ms, In-Memory) | Bon (Index B-Tree, ~1-5ms) | Bon pour point lookup (Partition Key requise) | Bon pour le voisinage (Index-Free Adjacency) |
| **Requêtes complexes** | Faible (Lua, RediSearch en option) | Très Bon (Aggregation Pipeline) | Très Faible (Pas de JOIN, pas d'ALLOW FILTERING) | Excellent (Parcours de graphe profond, GDS) |
| **Scalabilité** | Horizontale (Redis Cluster) | Horizontale (Sharding) | Massive et Linéaire (Masterless P2P) | Horizontale (Lecture), Verticale (Écriture) |
| **Use case idéal** | **Cache**, Sessions, Temps réel | **Documents**, CMS, E-commerce | **IoT**, **Logs**, Time Series (Séries Temporelles) | **Réseaux sociaux**, Fraude, Recommandation |

## Analyse des Performances (Basée sur l'exécution du script `benchmark.py`)

### 1. Benchmark Écriture
*   **Redis** : Grâce à l'utilisation d'un `pipeline`, Redis traite les écritures en masse directement en RAM en un seul aller-retour réseau. Il est invariablement le plus rapide sur des insertions brutes.
*   **MongoDB** : L'utilisation de `bulk_write` diminue drastiquement le surcoût réseau (network overhead). Les performances sont excellentes car le moteur de stockage (WiredTiger) écrit d'abord dans le cache en mémoire puis fait un flush asynchrone sur le disque (Journaling).
*   **Cassandra** : Conçu spécifiquement pour absorber des rafales d'écritures grâce à sa structure LSM-Tree (Memtable + CommitLog append-only). L'utilisation de `UNLOGGED BATCH` est recommandée pour accélérer l'insertion si et seulement si les données insérées appartiennent à la même partition.

### 2. Benchmark Lecture (Point Lookup)
*   **Redis** : L'accès O(1) en mémoire offre une latence sub-milliseconde constante.
*   **MongoDB** : Les requêtes `find_one({"_id": x})` utilisent l'index B-Tree natif de la Primary Key, offrant des performances d'environ 1 à 3ms, tant que le "Working Set" (les index et données fréquemment accédées) tient dans la RAM allouée.

### 3. Test de Charge Concurrente
*   **Comportement global** : La mise en place de 50 clients simultanés (Threads) expose la latence réseau et les capacités d'I/O. Redis gère cela parfaitement grâce à son Event Loop (multiplexage epoll) malgré son architecture monothread. MongoDB attribue un thread par connexion, ce qui implique un peu plus de contexte CPU.
*   **Goulots d'étranglement** : En Python, le GIL (Global Interpreter Lock) limite le parallélisme réel côté client ; ainsi, une partie de la dégradation mesurée provient du client lui-même. Côté Base de Données, un nœud unique Cassandra souffrira sous forte charge concurrente comparativement à un déploiement distribué où son architecture P2P brille réellement.

## Conclusion & Recommandation
Aucune base de données n'est "meilleure" dans l'absolu. L'architecture moderne impose la **Persistance Polyglotte** : choisir l'outil en fonction de la structure des données et des requêtes.

1.  **Données IoT / Capteurs (Insertions massives et continues)** → **Cassandra**.
2.  **Plateforme de mise en relation / Recommandation** → **Neo4j**.
3.  **Gestion de Dossiers Médicaux / Objets complexes (JSON)** → **MongoDB**.
4.  **Système de Cache ultra-rapide / File d'attente (Pub/Sub)** → **Redis**.
