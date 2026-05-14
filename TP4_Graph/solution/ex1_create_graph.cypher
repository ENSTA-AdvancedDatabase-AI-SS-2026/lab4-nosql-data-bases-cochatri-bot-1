// TP4 - Exercice 1 : Création du graphe UniConnect DZ

MATCH (n) DETACH DELETE n;

// 1.1 Contraintes
CREATE CONSTRAINT etudiant_id IF NOT EXISTS FOR (e:Etudiant) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cours_code IF NOT EXISTS FOR (c:Cours) REQUIRE c.code IS UNIQUE;
CREATE CONSTRAINT competence_nom IF NOT EXISTS FOR (c:Competence) REQUIRE c.nom IS UNIQUE;
CREATE CONSTRAINT club_nom IF NOT EXISTS FOR (c:Club) REQUIRE c.nom IS UNIQUE;
CREATE CONSTRAINT entreprise_nom IF NOT EXISTS FOR (e:Entreprise) REQUIRE e.nom IS UNIQUE;

// 1.2 Compétences
UNWIND [
  {nom: "Python", categorie: "Programmation"},
  {nom: "Java", categorie: "Programmation"},
  {nom: "SQL", categorie: "Bases de Données"},
  {nom: "NoSQL", categorie: "Bases de Données"},
  {nom: "Machine Learning", categorie: "IA"},
  {nom: "Deep Learning", categorie: "IA"},
  {nom: "React", categorie: "Web"},
  {nom: "Docker", categorie: "DevOps"},
  {nom: "Linux", categorie: "Systèmes"},
  {nom: "Réseaux", categorie: "Infrastructure"}
] AS comp
MERGE (:Competence {nom: comp.nom, categorie: comp.categorie});

// 1.3 Cours
UNWIND [
  {code: "INFO401", intitule: "Bases de Données Avancées", credits: 6, dept: "Informatique"},
  {code: "INFO402", intitule: "Intelligence Artificielle", credits: 6, dept: "Informatique"},
  {code: "INFO403", intitule: "Développement Web", credits: 4, dept: "Informatique"},
  {code: "INFO404", intitule: "Systèmes Distribués", credits: 5, dept: "Informatique"},
  {code: "INFO405", intitule: "Cloud Computing", credits: 4, dept: "Informatique"}
] AS cours
MERGE (:Cours {code: cours.code, intitule: cours.intitule, 
               credits: cours.credits, departement: cours.dept});

// Clubs & Entreprises
UNWIND [
  {nom: "Club IA USTHB", universite: "USTHB", domaine: "Intelligence Artificielle"},
  {nom: "Open Source USTO", universite: "USTO", domaine: "Logiciel Libre"},
  {nom: "Data Science Club", universite: "UMC", domaine: "Data Science"}
] AS club
MERGE (:Club {nom: club.nom, universite: club.universite, domaine: club.domaine});

UNWIND [
  {nom: "Sonatrach", secteur: "Energie", ville: "Alger"},
  {nom: "Yassir", secteur: "VTC & Tech", ville: "Alger"},
  {nom: "Mobilis", secteur: "Telecom", ville: "Alger"}
] AS ent
MERGE (:Entreprise {nom: ent.nom, secteur: ent.secteur, ville: ent.ville});

// 1.4 Étudiants
UNWIND [
  {id: "E001", prenom: "Ahmed", nom: "Bensalem", universite: "USTHB", filiere: "Informatique", annee: 3, ville: "Alger"},
  {id: "E002", prenom: "Fatima", nom: "Ouali", universite: "USTHB", filiere: "Informatique", annee: 3, ville: "Alger"},
  {id: "E003", prenom: "Yasmina", nom: "Derradji", universite: "USTO", filiere: "GL", annee: 2, ville: "Oran"},
  {id: "E004", prenom: "Amine", nom: "Saidi", universite: "UMC", filiere: "Informatique", annee: 4, ville: "Constantine"},
  {id: "E005", prenom: "Riad", nom: "Ziani", universite: "UMBB", filiere: "Electronique", annee: 3, ville: "Boumerdes"},
  {id: "E006", prenom: "Leila", nom: "Haddad", universite: "UBMA", filiere: "Mathématiques", annee: 1, ville: "Annaba"}
] AS data
MERGE (e:Etudiant {id: data.id})
SET e += data;

WITH range(7, 50) AS ids
UNWIND ids AS i
WITH i, 
     ["USTHB", "UMBB", "USTO", "UMC", "UBMA"][i % 5] AS univ,
     ["Informatique", "Mathématiques", "Electronique", "Telecoms", "GL"][i % 5] AS fil,
     ["Alger", "Boumerdes", "Oran", "Constantine", "Annaba"][i % 5] AS vil
MERGE (e:Etudiant {id: "E" + toString(i)})
SET e.prenom = "Prenom" + toString(i), 
    e.nom = "Nom" + toString(i), 
    e.universite = univ, 
    e.filiere = fil, 
    e.annee = (i % 5) + 1, 
    e.ville = vil;

// 1.5 Relations
// CONNAIT
MATCH (e1:Etudiant), (e2:Etudiant)
WHERE e1.id <> e2.id AND e1.universite = e2.universite AND rand() < 0.3
MERGE (e1)-[:CONNAIT {depuis: 2021 + toInteger(rand()*3)}]->(e2);

// S'assurer qu'Ahmed (E001) et Yasmina (E003) ont un chemin indirect
MATCH (e1:Etudiant {id: "E001"}), (e2:Etudiant {id: "E004"}), (e3:Etudiant {id: "E003"})
MERGE (e1)-[:CONNAIT {depuis: 2022}]->(e2)
MERGE (e2)-[:CONNAIT {depuis: 2023}]->(e3);

// SUIT
MATCH (e:Etudiant {filiere: "Informatique"}), (c:Cours)
WHERE rand() < 0.6
MERGE (e)-[:SUIT {semestre: "S" + toString(toInteger(rand()*6)+1), note: toInteger(rand()*10 + 10)}]->(c);

// MEMBRE_DE
MATCH (e:Etudiant), (c:Club)
WHERE e.universite = c.universite AND rand() < 0.4
MERGE (e)-[:MEMBRE_DE {role: "Membre"}]->(c);

// A_STAGE_CHEZ
MATCH (e:Etudiant), (ent:Entreprise)
WHERE rand() < 0.1
MERGE (e)-[:A_STAGE_CHEZ {annee: 2023, duree_mois: 3}]->(ent);

// MAITRISE
MATCH (e:Etudiant {filiere: "Informatique"}), (c:Competence)
WHERE rand() < 0.3
MERGE (e)-[:MAITRISE {niveau: ["Débutant", "Intermédiaire", "Avancé"][toInteger(rand()*3)]}]->(c);

// REQUIERT
MATCH (c:Cours {code: "INFO402"}), (comp:Competence {nom: "Machine Learning"})
MERGE (c)-[:REQUIERT]->(comp);

MATCH (c:Cours {code: "INFO401"}), (comp:Competence {nom: "NoSQL"})
MERGE (c)-[:REQUIERT]->(comp);
