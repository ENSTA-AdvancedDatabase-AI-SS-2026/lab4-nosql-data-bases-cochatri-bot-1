// TP4 - Exercice 4 : Requêtes Avancées

// 4.1 Trouver un tuteur
// "Étudiant en Master (annee >= 4) qui maîtrise Python et a eu >14/20 en BDD (INFO401)"
MATCH (tuteur:Etudiant)-[:MAITRISE]->(comp:Competence {nom: "Python"})
MATCH (tuteur)-[s:SUIT]->(cours:Cours {code: "INFO401"})
WHERE tuteur.annee >= 4 AND s.note > 14
RETURN tuteur.prenom, tuteur.nom, tuteur.universite, s.note AS note_bdd;

// 4.2 Réseau alumni dans une entreprise
// "Qui de mon réseau (jusqu'à 3 sauts) travaille chez Sonatrach ?"
MATCH (moi:Etudiant {prenom: "Ahmed"})-[:CONNAIT*1..3]-(alumni:Etudiant)-[:A_STAGE_CHEZ]->(ent:Entreprise {nom: "Sonatrach"})
WHERE moi <> alumni
RETURN DISTINCT alumni.prenom, alumni.nom, alumni.universite;

// 4.3 Détection de ponts
// Quels étudiants connectent des communautés isolées ?
// En guise d'approche simple sans algo GDS lourd : trouver les étudiants qui connaissent
// des étudiants d'au moins 3 universités différentes (connecteurs inter-universités).
MATCH (e:Etudiant)-[:CONNAIT]-(ami:Etudiant)
WITH e, count(DISTINCT ami.universite) AS universites_connectees
WHERE universites_connectees > 1
RETURN e.prenom, e.nom, e.universite, universites_connectees
ORDER BY universites_connectees DESC;

// 4.4 Analyse temporelle
// Croissance du réseau : nouvelles connexions par année (puisque notre attribut 'depuis' est l'année)
MATCH ()-[c:CONNAIT]->()
RETURN c.depuis AS annee_connexion, count(c) / 2 AS nouvelles_connexions
// On divise par 2 car MERGE crée une relation orientée, mais souvent les connexions sociales sont comptées une fois par paire.
ORDER BY annee_connexion;

// 4.5 Score de similarité
// Étudiants les plus similaires à Ahmed (cours, compétences, clubs) - Coefficient de Jaccard
// Vrai Jaccard (sans APOC) : Jaccard = Intersection / (Taille_A + Taille_B - Intersection)
MATCH (ahmed:Etudiant {prenom: "Ahmed"})-[:SUIT|MAITRISE|MEMBRE_DE]->(entite)<-[:SUIT|MAITRISE|MEMBRE_DE]-(autre:Etudiant)
WITH ahmed, autre, count(DISTINCT entite) AS intersection
MATCH (ahmed)-[:SUIT|MAITRISE|MEMBRE_DE]->(e1)
WITH ahmed, autre, intersection, count(DISTINCT e1) AS taille_ahmed
MATCH (autre)-[:SUIT|MAITRISE|MEMBRE_DE]->(e2)
WITH autre, intersection, taille_ahmed, count(DISTINCT e2) AS taille_autre
WITH autre, intersection, taille_ahmed, taille_autre,
     (intersection * 1.0) / (taille_ahmed + taille_autre - intersection) AS jaccard
RETURN autre.prenom, autre.nom, jaccard
ORDER BY jaccard DESC
LIMIT 5;
