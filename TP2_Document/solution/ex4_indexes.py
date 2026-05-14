import pymongo
from pprint import pprint

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_db"]

# 4.1 Create indexes
print("=== 4.1 Création des index ===")
# Index 1 : Recherche fréquente par wilaya + antécédents
db.patients.create_index([("adresse.wilaya", pymongo.ASCENDING), ("antecedents", pymongo.ASCENDING)])
print("Index composé créé sur (adresse.wilaya, antecedents)")

# Index 2 : Recherche par date de consultation
db.patients.create_index([("consultations.date", pymongo.ASCENDING)])
print("Index créé sur consultations.date")

# Index 3 : Texte sur diagnostics
db.patients.create_index([("consultations.diagnostic", pymongo.TEXT)])
print("Index textuel créé sur consultations.diagnostic")

# Index 4 : Analyses par patient (lookup)
db.analyses.create_index([("patient_id", pymongo.ASCENDING)])
print("Index créé sur analyses.patient_id")

# 4.2 Explain
print("\n=== 4.2 Comparaison avec explain() ===")
# Supprimer l'index temporairement pour tester AVANT
db.patients.drop_index("adresse.wilaya_1_antecedents_1")

requete_test = {
    "adresse.wilaya": "Alger",
    "antecedents": "Diabète type 2"
}

explain_avant = db.command('explain', {'find': 'patients', 'filter': requete_test}, verbosity='executionStats')
print("\nAVANT index :")
print("nReturned:", explain_avant['executionStats']['nReturned'])
print("totalDocsExamined:", explain_avant['executionStats']['totalDocsExamined'])
print("executionTimeMillis:", explain_avant['executionStats']['executionTimeMillis'])

# Recréer l'index
db.patients.create_index([("adresse.wilaya", pymongo.ASCENDING), ("antecedents", pymongo.ASCENDING)])

explain_apres = db.command('explain', {'find': 'patients', 'filter': requete_test}, verbosity='executionStats')
print("\nAPRÈS index :")
print("nReturned:", explain_apres['executionStats']['nReturned'])
print("totalDocsExamined:", explain_apres['executionStats']['totalDocsExamined'])
print("executionTimeMillis:", explain_apres['executionStats']['executionTimeMillis'])

# 4.4 Index TTL
print("\n=== 4.4 Index TTL ===")
# expirer après 5 ans (157680000 secondes)
db.analyses.create_index(
    [("date", pymongo.ASCENDING)],
    expireAfterSeconds=157680000
)
print("Index TTL créé sur analyses.date (5 ans)")
