-- TP3 - Exercice 4 : Compaction et Maintenance
USE smartgrid;

-- 4.1 Choisir la stratégie de compaction pour chaque table
-- Pour les mesures (séries temporelles) : TimeWindowCompactionStrategy (TWCS) est la meilleure.
-- Pourquoi ? TWCS regroupe les données par fenêtres de temps (ex: 1 jour).
-- Quand la fenêtre est passée, le fichier SSTable n'est plus compacté avec les nouvelles données.
-- C'est très performant pour les requêtes sur des plages de temps récentes (Time Series)
-- et ça rend l'expiration via TTL très efficace (un fichier SSTable complet est supprimé sans I/O supplémentaire).

-- 4.2 Configurer TWCS pour les mesures
ALTER TABLE mesures_par_capteur
WITH compaction = {
  'class': 'TimeWindowCompactionStrategy',
  'compaction_window_unit': 'DAYS',
  'compaction_window_size': 1
};

-- 4.3 Vérifier l'utilisation des TTL
-- Requête pour voir la durée de vie restante sur une ligne spécifique.
-- La fonction TTL() doit être appelée sur une colonne qui ne fait pas partie de la Primary Key.
SELECT capteur_id, timestamp, TTL(tension_v) FROM mesures_par_capteur
LIMIT 10;

-- 4.4 Analyser une partition "hot" : comment la détecter et la corriger ?
-- 1. Détecter : Utiliser la commande Cassandra `nodetool toppartitions smartgrid alertes_par_wilaya` ou `nodetool tablestats`.
--    Une hot partition se voit par une taille disproportionnée par rapport aux autres partitions.
-- 2. Corriger : Il faut redéfinir la Partition Key (bucketization).
--    Si la clé de partition n'était que `wilaya`, la partition "Alger" grossirait à l'infini (Hot Partition).
--    La solution est d'utiliser `PRIMARY KEY ((wilaya, date_jour), timestamp)`. 
--    Ceci force la création d'une nouvelle partition par wilaya CHAQUE JOUR. 
--    (Nous l'avons implémenté ainsi dès l'Ex1).
