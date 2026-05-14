-- TP4 - Exercice 3 : Algorithmes de Graphe avec GDS

-- ─── 3.1 : PLUS COURT CHEMIN ─────────────────────────────────────
-- "Ahmed → Yasmina"

MATCH p = shortestPath(
  (a:Etudiant {prenom: "Ahmed"})-[:CONNAIT*..10]-(b:Etudiant {prenom: "Yasmina"})
)
RETURN 
  [n IN nodes(p) | n.prenom + " (" + n.universite + ")"] AS chemin,
  length(p) AS distance;


-- ─── 3.2 : CENTRALITÉ DE DEGRÉ ───────────────────────────────────

CALL gds.graph.project(
  'reseau_social',
  'Etudiant',
  'CONNAIT'
);

CALL gds.degree.stream('reseau_social')
YIELD nodeId, score
RETURN 
  gds.util.asNode(nodeId).prenom AS etudiant,
  gds.util.asNode(nodeId).universite AS universite,
  score AS nb_connexions
ORDER BY nb_connexions DESC
LIMIT 10;


-- ─── 3.3 : COMMUNAUTÉS (LOUVAIN) ────────────────────────────────

CALL gds.louvain.stream('reseau_social')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId).prenom) AS membres
RETURN 
  communityId,
  size(membres) AS taille,
  membres[0..5] AS exemple_membres
ORDER BY taille DESC;


-- ─── 3.4 : RECOMMANDATION DE CONTACTS ───────────────────────────

MATCH (moi:Etudiant {prenom: "Ahmed"})

OPTIONAL MATCH (moi)-[:CONNAIT]-(ami)-[:CONNAIT]-(suggestion:Etudiant)
WHERE suggestion <> moi

OPTIONAL MATCH (moi)-[:SUIT]->(c:Cours)<-[:SUIT]-(suggestion)

WITH suggestion,
     count(DISTINCT ami) AS amis_communs,
     count(DISTINCT c) AS cours_communs,
     CASE 
        WHEN suggestion.filiere = moi.filiere THEN 1
        ELSE 0
     END AS meme_filiere

WITH suggestion,
     (amis_communs * 3 + cours_communs * 2 + meme_filiere) AS score

RETURN 
  suggestion.prenom AS etudiant,
  suggestion.universite AS universite,
  score
ORDER BY score DESC
LIMIT 5;


-- ─── 3.5 : CHEMIN COMPÉTENCES ───────────────────────────────────

MATCH path = (debut:Cours)-[:REQUIERT*]->(but:Competence {nom: "Machine Learning"})
RETURN 
  [n IN nodes(path) | 
    CASE 
      WHEN n:Cours THEN n.intitule 
      ELSE n.nom 
    END
  ] AS parcours_apprentissage;


-- ─── CLEANUP ────────────────────────────────────────────────────
CALL gds.graph.drop('reseau_social');
