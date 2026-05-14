# Rapport TP4 - Neo4j (UniConnect DZ)

## 1. Schéma du Graphe

Le graphe est articulé autour de 5 étiquettes principales (Labels) et de 5 types de relations :

**Nœuds :**
- `(Etudiant)` : Représente les utilisateurs de la plateforme.
- `(Cours)` : Les matières enseignées.
- `(Competence)` : Les savoir-faire ou technologies.
- `(Club)` : Les associations étudiantes.
- `(Entreprise)` : Les sociétés accueillant les stagiaires.

**Relations :**
- `(Etudiant)-[:CONNAIT]->(Etudiant)` : Lien social d'amitié/connexion.
- `(Etudiant)-[:SUIT]->(Cours)` : Suivi académique avec l'attribut `note`.
- `(Etudiant)-[:MAITRISE]->(Competence)` : Compétences acquises avec le niveau.
- `(Etudiant)-[:MEMBRE_DE]->(Club)` : Engagement associatif.
- `(Etudiant)-[:A_STAGE_CHEZ]->(Entreprise)` : Parcours professionnel.
- `(Cours)-[:REQUIERT]->(Competence)` : Pré-requis ou compétences enseignées.

## 2. Résultats de l'Algorithme de Communautés (Louvain)

L'algorithme de Louvain identifie des "cercles sociaux" (communautés) en maximisant la modularité du graphe (densité des liens à l'intérieur d'une communauté par rapport aux liens extérieurs).
Dans le graphe simulé d'UniConnect DZ, les communautés qui se dégagent ont tendance à se regrouper géographiquement et académiquement. Lors de la génération des relations `CONNAIT`, nous avons favorisé les connexions intra-universités. 
Par conséquent, la requête GDS Louvain retourne généralement 5 grandes communautés, correspondant de manière évidente aux bassins de population étudiante : l'une centrée sur l'USTHB (Alger), une autre sur l'USTO (Oran), l'UMC (Constantine), l'UMBB (Boumerdes) et l'UBMA (Annaba). Des connecteurs (ponts) mineurs lient ces groupes.

## 3. Comparaison : Requête d'amis d'amis (SQL vs Cypher)

**Requête cible :** "Amis d'amis d'Ahmed qui ne sont pas déjà ses amis"

**En SQL (Base Relationnelle) :**
```sql
SELECT DISTINCT fof.id, fof.prenom 
FROM Etudiant a
JOIN Connait c1 ON a.id = c1.id_etudiant1
JOIN Connait c2 ON c1.id_etudiant2 = c2.id_etudiant1
JOIN Etudiant fof ON c2.id_etudiant2 = fof.id
WHERE a.prenom = 'Ahmed' 
  AND fof.id != a.id
  AND fof.id NOT IN (
      SELECT id_etudiant2 FROM Connait WHERE id_etudiant1 = a.id
  );
```
*Complexité* : O(N²) ou O(N³) au minimum. Les `JOIN` multiples sont très coûteux, en particulier si la table d'association `Connait` contient des millions d'entrées. La sous-requête avec `NOT IN` (anti-join) dégrade encore considérablement les performances.
*Lisibilité* : Complexe, verbeuse et sujette aux erreurs (la gestion des relations bi-directionnelles en SQL nécessite des clauses UNION complexes).

**En Cypher (Base Graphe) :**
```cypher
MATCH (ahmed:Etudiant {prenom: "Ahmed"})-[:CONNAIT]-()-[:CONNAIT]-(fof:Etudiant)
WHERE NOT (ahmed)-[:CONNAIT]-(fof) AND ahmed <> fof
RETURN DISTINCT fof.prenom, fof.nom;
```
*Complexité* : Traversée locale en O(k²) où *k* est le nombre moyen d'amis par personne. Neo4j ne fait pas de scans de tables ni d'intersections d'ensembles massifs ; il suit simplement les "pointeurs" physiques en mémoire (Index-Free Adjacency). Cela répond instantanément même avec des millions d'utilisateurs.
*Lisibilité* : Très intuitive, la syntaxe dessine littéralement le motif du chemin qu'on cherche à retrouver : `()-[]-()`.
