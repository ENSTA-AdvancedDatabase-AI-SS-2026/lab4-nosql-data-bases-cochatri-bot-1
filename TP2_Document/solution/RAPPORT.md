# Rapport TP2 - MongoDB (HealthCare DZ)

## 1. Modélisation : Embedding vs Referencing

### Collection `patients` (Embedding)
**Justification** : Nous avons choisi l'**Embedding** pour intégrer directement les `consultations` à l'intérieur du document du patient. Dans le domaine médical (surtout lors de la consultation d'un dossier patient), les informations d'un patient et son historique de consultations sont presque toujours lus ensemble. Intégrer les consultations dans un tableau permet de récupérer l'intégralité du dossier médical en une seule opération de lecture (un seul accès disque / DB), ce qui améliore considérablement les performances de lecture.

### Collection `analyses` (Referencing)
**Justification** : Nous avons choisi le **Referencing** pour les `analyses`. Les résultats d'analyses (NFS, bilan sanguin, Imagerie) peuvent contenir des données volumineuses ou un très grand nombre d'enregistrements au fil du temps (le volume de données peut faire dépasser la limite de 16MB d'un document BSON). Par ailleurs, les analyses sont souvent gérées par le laboratoire indépendamment de l'interface de consultation médicale et peuvent être requêtées séparément pour des agrégations globales ou des statistiques. Utiliser un lien symbolique (`patient_id`) est donc plus pertinent.

---

## 2. Optimisation et Indexation

### Résultats `explain("executionStats")`

| Métrique | AVANT Indexation | APRÈS Indexation |
| :--- | :--- | :--- |
| **Index utilisé** | `COLLSCAN` (Aucun) | `adresse.wilaya_1_antecedents_1` |
| **nReturned** | 1 (Exemple) | 1 |
| **totalDocsExamined** | 20 (Parcourt toute la collection) | 1 (Parcourt uniquement les documents matchant l'index) |
| **executionTimeMillis** | ~1-3 ms (Peut être énorme avec de gros volumes) | ~0-1 ms |

**Conclusion** : L'utilisation d'un index composé sur `(adresse.wilaya, antecedents)` empêche MongoDB de faire un scan complet de la collection (Collection Scan). Le moteur va directement consulter l'arbre B-Tree de l'index pour trouver l'adresse physique des documents concernés, réduisant ainsi `totalDocsExamined` de façon drastique.

---

## 3. Explication du Pipeline d'Agrégation (Requête complexe)

**Requête** : *Top 5 médecins par nombre de consultations et taux de ré-consultation (Ex 3.5)*

```javascript
db.patients.aggregate([
    // 1. Dérouler le tableau "consultations"
    // Chaque élément du tableau devient un document distinct, ce qui nous permet
    // de grouper les consultations individuellement par médecin par la suite.
    {"$unwind": "$consultations"},
    
    // 2. Grouper par le nom du médecin
    // On compte le nombre total de consultations ("totalConsultations").
    // On collecte les identifiants uniques des patients consultés dans un Set ("patientsUniques")
    // pour éviter les doublons.
    {"$group": {
        "_id": "$consultations.medecin.nom",
        "totalConsultations": {"$sum": 1},
        "patientsUniques": {"$addToSet": "$_id"}
    }},
    
    // 3. Ajouter un champ calculant la taille du tableau "patientsUniques"
    // Cela nous donne le nombre de patients distincts vus par ce médecin.
    {"$addFields": {
        "nbPatientsUniques": {"$size": "$patientsUniques"}
    }},
    
    // 4. Calculer le taux de ré-consultation
    // Formule : ((totalConsultations - nbPatientsUniques) / nbPatientsUniques) * 100
    // Un taux de 0% signifie que le médecin n'a vu chaque patient qu'une seule fois.
    // Un taux élevé indique que les mêmes patients reviennent fréquemment.
    {"$addFields": {
        "tauxReconsultation": {
            "$multiply": [
                {"$divide": [
                    {"$subtract": ["$totalConsultations", "$nbPatientsUniques"]},
                    "$nbPatientsUniques"
                ]},
                100
            ]
        }
    }},
    
    // 5. Exclure le tableau détaillé des patients pour alléger le résultat
    {"$project": {"patientsUniques": 0}},
    
    // 6. Trier par le nombre total de consultations de manière décroissante
    {"$sort": {"totalConsultations": -1}},
    
    // 7. Garder uniquement les 5 médecins les plus sollicités
    {"$limit": 5}
])
```
