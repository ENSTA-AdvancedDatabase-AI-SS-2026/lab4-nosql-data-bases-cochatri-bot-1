import pymongo
from pprint import pprint

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_db"]

print("=== 5.1 : Dossier complet d'un patient (Patients + Analyses) ===")
# On prend un patient au hasard qui a des analyses
dossier_complet = list(db.patients.aggregate([
    {
        "$lookup": {
            "from": "analyses",
            "localField": "_id",
            "foreignField": "patient_id",
            "as": "dossier_analyses"
        }
    },
    {"$match": {"dossier_analyses.0": {"$exists": True}}},
    {"$limit": 1}
]))
pprint(dossier_complet)


print("\n=== 5.2 : Patients dont la glycémie > 1.26 g/L ===")
# On part de la collection analyses
patients_glycemie = list(db.analyses.aggregate([
    {"$match": {
        "type": "Glycémie",
        "resultats.valeur": {"$gt": 1.26}
    }},
    {
        "$lookup": {
            "from": "patients",
            "localField": "patient_id",
            "foreignField": "_id",
            "as": "patient_details"
        }
    },
    {"$unwind": "$patient_details"},
    {"$project": {
        "_id": 0,
        "patient": {"$concat": ["$patient_details.nom", " ", "$patient_details.prenom"]},
        "valeur_glycemie": "$resultats.valeur",
        "date_analyse": "$date"
    }}
]))
pprint(patients_glycemie)


print("\n=== 5.3 : Statistiques croisées : taux d'analyses anormales par wilaya ===")
# Hypothèse : on considère une analyse anormale si sa valeur dépasse un certain seuil.
# Pour le test, disons que si 'valeur' existe et est > 1.2, c'est anormal.
stats_croisees = list(db.analyses.aggregate([
    {
        "$lookup": {
            "from": "patients",
            "localField": "patient_id",
            "foreignField": "_id",
            "as": "patient"
        }
    },
    {"$unwind": "$patient"},
    {"$addFields": {
        "est_anormale": {
            "$cond": [{"$gt": ["$resultats.valeur", 1.2]}, 1, 0]
        }
    }},
    {"$group": {
        "_id": "$patient.adresse.wilaya",
        "total_analyses": {"$sum": 1},
        "analyses_anormales": {"$sum": "$est_anormale"}
    }},
    {"$addFields": {
        "taux_anormalite_pourcentage": {
            "$multiply": [{"$divide": ["$analyses_anormales", "$total_analyses"]}, 100]
        }
    }},
    {"$sort": {"taux_anormalite_pourcentage": -1}}
]))
pprint(stats_croisees)
