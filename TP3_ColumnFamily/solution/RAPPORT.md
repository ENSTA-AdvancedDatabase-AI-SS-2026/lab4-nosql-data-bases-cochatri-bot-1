# Rapport TP3 - Cassandra (SmartGrid DZ)

## 1. Justification de chaque Partition Key (Risque de Hot Partition ?)

*   **`mesures_par_capteur`** :
    *   *Partition Key* : `(capteur_id, date_jour)`
    *   *Justification* : Un seul capteur générant 1 mesure par minute produira 1440 mesures par jour. Cela forme une partition d'une taille très raisonnable. L'ajout de `date_jour` ("bucketization") est crucial car sans cela, la partition d'un capteur grossirait indéfiniment au fil des années (devenant une "Hot Partition" à terme, limitant les performances). Avec la date, on garantit une distribution équilibrée et une taille maximale de partition.
*   **`alertes_par_wilaya`** :
    *   *Partition Key* : `(wilaya, date_jour)`
    *   *Justification* : Grouper les alertes uniquement par `wilaya` créerait un déséquilibre majeur. La wilaya d'Alger générera bien plus d'alertes que d'autres (Hot Partition spatiale). Pour lisser cela, on utilise la bucketization par jour `(wilaya, date_jour)`. Ainsi, même pour Alger, les données sont divisées en petits segments journaliers, empêchant une partition de devenir trop grosse et assurant une suppression aisée via TTL au bout d'un an.
*   **`agregats_horaires`** :
    *   *Partition Key* : `(wilaya)`
    *   *Justification* : Étant donné qu'il ne s'agit que d'agrégats calculés par heure, la volumétrie est très faible (24 lignes par jour par wilaya, soit 8760 lignes par an). Dans ce cas spécifique, une clé de partition simple `(wilaya)` ne pose pas de risque immédiat de "Hot Partition", bien qu'il faille le surveiller à long terme (5 ans de TTL = 43800 lignes max par partition).

## 2. Pourquoi `ALLOW FILTERING` est dangereux en production

La clause `ALLOW FILTERING` permet à Cassandra d'exécuter une requête pour laquelle il ne peut pas utiliser efficacement la clé de partition (ex: faire un filtrage sur une colonne qui n'est ni clé de partition ni d'index secondaire).

**Pourquoi c'est dangereux :**
Cassandra devra lire (scanner) potentiellement **toutes les partitions sur tous les nœuds** du cluster pour ramener les quelques lignes qui correspondent au filtre. C'est l'équivalent d'un Full Table Scan distribué.
*   Cela engendre une énorme quantité d'I/O (lecture disque).
*   Cela provoque une sur-consommation de CPU et de réseau (transfert des données inter-nœuds).
*   En production (Big Data), cela résulte systématiquement en un Timeout (la requête met trop de temps à répondre) et peut même faire tomber un nœud sous la charge.
*   *Solution* : En Cassandra, on **modélise la requête, pas les données**. S'il faut chercher par un nouveau filtre, on crée une table dédiée ou une Materialized View.

## 3. Comparaison TWCS vs STCS vs LCS : quand utiliser chacun ?

| Stratégie de Compaction | Fonctionnement | Cas d'usage privilégié |
| :--- | :--- | :--- |
| **STCS** (SizeTieredCompactionStrategy) | Regroupe les SSTables de taille similaire entre elles. C'est la stratégie par défaut. | Charges de travail avec **beaucoup d'insertions** pures (write-heavy) sans considérations temporelles spécifiques. |
| **LCS** (LeveledCompactionStrategy) | Maintient une hiérarchie stricte de niveaux de taille fixe, garantissant très peu de chevauchements. | Charges de travail avec **beaucoup de lectures aléatoires** (read-heavy) et de mises à jour fréquentes (updates/deletes). |
| **TWCS** (TimeWindowCompactionStrategy) | Regroupe les SSTables par intervalles de temps fixes (ex: jours, semaines). Les données expirées (TTL) sont jetées en une seule fois sans surcoût d'E/S. | Données de **Séries Temporelles (Time Series) / IoT**. Données écrites séquentiellement qui ne sont plus modifiées et qui expirent naturellement (TTL). |

**Conclusion pour SmartGrid DZ** : Les capteurs IoT insèrent des séries temporelles immuables soumises à des TTL (90 jours, 1 an, 5 ans). TWCS est de loin le choix optimal car il évite la fragmentation et rend l'expiration des données presque gratuite (Cassandra efface simplement un vieux fichier sur disque).
