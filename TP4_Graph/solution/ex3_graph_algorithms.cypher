// TP4 - Exercice 3 : Algorithmes de Graphe avec GDS
// Prérequis : Plugin Graph Data Science installé

// 3.1 Plus court chemin
MATCH p = shortestPath(
  (a:Etudiant {prenom: "Ahmed"})-[:CONNAIT*..10]-(b:Etudiant {prenom: "Yasmina"})
)
RETURN [n IN nodes(p) | n.prenom + " (" + n.universite + ")"] AS chemin,
       length(p) AS nb_intermediaires;

// Projection du graphe
// On vérifie d'abord s'il existe et on le supprime si c'est le cas (pour pouvoir relancer le script)
CALL gds.graph.drop('reseau_social', false);

CALL gds.graph.project(
  'reseau_social',
  'Etudiant',
  {
    CONNAIT: {
      orientation: 'UNDIRECTED'
    }
  }
);

// 3.2 Centralité de degré (Étudiants les plus connectés)
CALL gds.degree.stream('reseau_social')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).prenom AS etudiant,
       gds.util.asNode(nodeId).universite AS universite,
       score AS nb_connexions
ORDER BY score DESC
LIMIT 10;

// 3.3 Détection de communautés (Louvain)
CALL gds.louvain.stream('reseau_social')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId).prenom) AS membres
RETURN communityId,
       size(membres) AS taille,
       membres[0..5] AS exemple_membres
ORDER BY taille DESC;

// 3.4 Recommandation de contacts
// Score = nb_amis_communs * 3 + nb_cours_communs * 2 + (meme_filiere ? 1 : 0)
MATCH (moi:Etudiant {prenom: "Ahmed"}), (autre:Etudiant)
WHERE moi <> autre AND NOT (moi)-[:CONNAIT]-(autre)
OPTIONAL MATCH (moi)-[:CONNAIT]-(ami)-[:CONNAIT]-(autre)
WITH moi, autre, count(DISTINCT ami) AS amis_communs
OPTIONAL MATCH (moi)-[:SUIT]->(c:Cours)<-[:SUIT]-(autre)
WITH moi, autre, amis_communs, count(DISTINCT c) AS cours_communs
WITH moi, autre, amis_communs, cours_communs,
     CASE WHEN moi.filiere = autre.filiere THEN 1 ELSE 0 END AS meme_filiere_score
WITH autre, (amis_communs * 3) + (cours_communs * 2) + meme_filiere_score AS score
WHERE score > 0
RETURN autre.prenom AS suggestion, autre.universite AS universite, score
ORDER BY score DESC
LIMIT 5;

// 3.5 Chemin de compétences
MATCH path = (debut:Cours)-[:REQUIERT*]->(but:Competence {nom: "Machine Learning"})
RETURN [n IN nodes(path) | 
  CASE WHEN 'Cours' IN labels(n) THEN n.intitule ELSE n.nom END
] AS parcours_apprentissage;

// Nettoyage
CALL gds.graph.drop('reseau_social', false);
