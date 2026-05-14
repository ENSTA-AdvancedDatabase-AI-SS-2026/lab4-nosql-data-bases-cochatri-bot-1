-- TP4 - Exercice 1 : Création du graphe UniConnect DZ

-- ─── CLEAN DATABASE ─────────────────────────────────────────────
MATCH (n) DETACH DELETE n;


-- ─── 1.1 : CONSTRAINTS ───────────────────────────────────────────
CREATE CONSTRAINT etudiant_id IF NOT EXISTS
FOR (e:Etudiant)
REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT cours_code IF NOT EXISTS
FOR (c:Cours)
REQUIRE c.code IS UNIQUE;

CREATE CONSTRAINT competence_nom IF NOT EXISTS
FOR (c:Competence)
REQUIRE c.nom IS UNIQUE;


-- ─── 1.2 : COMPETENCES ───────────────────────────────────────────
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


-- ─── 1.3 : COURS ────────────────────────────────────────────────
UNWIND [
  {code: "INFO401", intitule: "Bases de Données Avancées", credits: 6, dept: "Informatique"},
  {code: "INFO402", intitule: "Intelligence Artificielle", credits: 6, dept: "Informatique"},
  {code: "INFO403", intitule: "Développement Web", credits: 4, dept: "Informatique"},
  {code: "INFO404", intitule: "Systèmes Distribués", credits: 5, dept: "Informatique"},
  {code: "INFO405", intitule: "Cloud Computing", credits: 4, dept: "Informatique"}
] AS cours
MERGE (:Cours {
  code: cours.code,
  intitule: cours.intitule,
  credits: cours.credits,
  departement: cours.dept
});


-- ─── 1.4 : 50 ÉTUDIANTS ──────────────────────────────────────────
UNWIND [
  {id:"E001",prenom:"Ahmed",nom:"Bensalem",universite:"USTHB",filiere:"Informatique",annee:3,ville:"Alger"},
  {id:"E002",prenom:"Fatima",nom:"Ouali",universite:"USTHB",filiere:"Informatique",annee:3,ville:"Alger"},
  {id:"E003",prenom:"Yacine",nom:"Khelifi",universite:"UMBB",filiere:"Mathématiques",annee:2,ville:"Boumerdes"},
  {id:"E004",prenom:"Imane",nom:"Belaid",universite:"USTO",filiere:"Electronique",annee:3,ville:"Oran"},
  {id:"E005",prenom:"Omar",nom:"Djebbar",universite:"UMC",filiere:"Telecoms",annee:2,ville:"Constantine"},
  {id:"E006",prenom:"Sara",nom:"Zerrouki",universite:"UBMA",filiere:"GL",annee:1,ville:"Annaba"},
  {id:"E007",prenom:"Karim",nom:"Hamidi",universite:"USTHB",filiere:"Informatique",annee:4,ville:"Alger"},
  {id:"E008",prenom:"Nadia",nom:"Fares",universite:"USTO",filiere:"Informatique",annee:2,ville:"Oran"},
  {id:"E009",prenom:"Ali",nom:"Cherif",universite:"UMBB",filiere:"GL",annee:3,ville:"Boumerdes"},
  {id:"E010",prenom:"Lina",nom:"Boudjemaa",universite:"UMC",filiere:"Mathématiques",annee:1,ville:"Constantine"}
] +
[
// auto-generated students E011 → E050
...Array.from({length:40}, (_,i)=>({
  id:`E${String(i+11).padStart(3,"0")}`,
  prenom:["Ahmed","Ali","Omar","Yasmine","Nour","Imane","Rania"][i%7],
  nom:["Benali","Kaci","Mokrani","Bensalem","Derrar","Saidi"][i%6],
  universite:["USTHB","UMBB","USTO","UMC","UBMA"][i%5],
  filiere:["Informatique","GL","Mathématiques","Electronique","Telecoms"][i%5],
  annee:(i%5)+1,
  ville:["Alger","Oran","Constantine","Annaba","Blida"][i%5]
}))
] AS data
MERGE (e:Etudiant {id: data.id})
SET e += data;


-- ─── 1.5 : RELATIONS ────────────────────────────────────────────

-- CONNAIT (peer connections)
UNWIND range(1, 50) AS i
MATCH (e1:Etudiant {id: "E001"})
MATCH (e2:Etudiant {id: "E00" + (i+1)})
WHERE e2 IS NOT NULL AND e1 <> e2
MERGE (e1)-[:CONNAIT]->(e2);


-- SUIT (courses with grades)
UNWIND range(1, 50) AS i
MATCH (e:Etudiant {id: "E00" + i})
MATCH (c:Cours)
WITH e, c
WHERE rand() < 0.6
MERGE (e)-[r:SUIT]->(c)
SET r.note = 10 + rand()*10;


-- MAITRISE (skills)
MATCH (e:Etudiant)
MATCH (comp:Competence)
WITH e, comp
WHERE rand() < 0.4
MERGE (e)-[m:MAITRISE]->(comp)
SET m.niveau = toInteger(1 + rand()*5);


-- ─── VERIFICATION ───────────────────────────────────────────────
MATCH (n)
RETURN labels(n)[0] AS type, count(*) AS total
ORDER BY total DESC;

MATCH ()-[r]->()
RETURN type(r) AS relation, count(*) AS total
ORDER BY total DESC;
