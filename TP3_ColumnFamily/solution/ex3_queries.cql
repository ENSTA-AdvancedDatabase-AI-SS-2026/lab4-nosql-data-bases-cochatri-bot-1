-- TP3 - Exercice 3 : Requêtes CQL
USE smartgrid;

-- 3.1 Mesures d'un capteur spécifique sur les dernières 6 heures
-- (Remplacez les UUIDs et dates par des valeurs réelles issues de votre base)
SELECT * FROM mesures_par_capteur
WHERE capteur_id = 123e4567-e89b-12d3-a456-426614174000
  AND date_jour = '2024-05-14'
  AND timestamp >= '2024-05-14 06:00:00';

-- 3.2 Dernière mesure de chaque capteur d'une wilaya
-- Pour obtenir la dernière mesure d'un capteur précis, on utilise LIMIT 1.
-- Puisque notre table mesures_par_capteur a un CLUSTERING ORDER BY (timestamp DESC),
-- le premier résultat retourné sera le plus récent.
SELECT * FROM mesures_par_capteur
WHERE capteur_id = 123e4567-e89b-12d3-a456-426614174000
  AND date_jour = '2024-05-14'
LIMIT 1;

-- 3.3 Capteurs en alerte dans la wilaya "Alger" aujourd'hui
-- Compter
SELECT count(*) FROM alertes_par_wilaya
WHERE wilaya = 'Alger' AND date_jour = '2024-05-14';

-- Lister
SELECT capteur_id, code_alerte, timestamp FROM alertes_par_wilaya
WHERE wilaya = 'Alger' AND date_jour = '2024-05-14';

-- 3.4 Consommation totale par heure sur une journée (dashboard)
SELECT date_heure, puissance_moy_kw FROM agregats_horaires
WHERE wilaya = 'Alger'
  AND date_heure >= '2024-05-14 00:00:00'
  AND date_heure <= '2024-05-14 23:59:59';

-- 3.5 Détection d'anomalie : capteurs avec tension < 200V ou > 240V
-- Note: Exécuter cette requête sur mesures_par_capteur nécessiterait ALLOW FILTERING.
-- C'est pourquoi nous avons modélisé les anomalies directement dans la table alertes_par_wilaya lors de l'ingestion !
SELECT * FROM alertes_par_wilaya
WHERE wilaya = 'Alger' AND date_jour = '2024-05-14';


-- 3.7 Requête ALLOW FILTERING : Pourquoi éviter ?
-- Si nous faisions :
-- SELECT * FROM mesures_par_capteur WHERE tension_v > 240 ALLOW FILTERING;
-- Cassandra lirait TOUTE la base de données, partition par partition, sur chaque nœud, 
-- pour appliquer le filtre. Cela entraînerait un timeout et une dégradation des performances.

-- Requête correcte (Modéliser la requête, pas l'entité) :
-- On lit directement depuis la table des alertes pré-filtrées.
SELECT capteur_id, description, timestamp FROM alertes_par_wilaya
WHERE wilaya = 'Alger' AND date_jour = '2024-05-14';
