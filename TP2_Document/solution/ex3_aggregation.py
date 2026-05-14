import pymongo
from pprint import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_db"]

print("=== 3.1 : Top diagnostics par wilaya ===")
diag_par_wilaya = list(db.patients.aggregate([
    {"$unwind": "$consultations"},
    {"$group": {
        "_id": {
            "wilaya": "$adresse.wilaya",
            "diagnostic": "$consultations.diagnostic"
        },
        "count": {"$sum": 1}
    }},
    {"$project": {
        "_id": 0,
        "wilaya": "$_id.wilaya",
        "diagnostic": "$_id.diagnostic",
        "count": 1
    }},
    {"$sort": {"count": -1}},
    {"$limit": 20}
]))
pprint(diag_par_wilaya)

print("\n=== 3.2 : Médicament le plus prescrit par spécialité ===")
meds_par_specialite = list(db.patients.aggregate([
    {"$unwind": "$consultations"},
    {"$unwind": "$consultations.medicaments"},
    {"$group": {
        "_id": {
            "specialite": "$consultations.medecin.specialite",
            "medicament": "$consultations.medicaments.nom"
        },
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}},
    {"$group": {
        "_id": "$_id.specialite",
        "topMedicament": {"$first": "$_id.medicament"},
        "count": {"$first": "$count"}
    }}
]))
pprint(meds_par_specialite)

print("\n=== 3.3 : Évolution mensuelle des consultations (12 derniers mois) ===")
date_un_an = datetime.now() - relativedelta(years=1)

evolution_mensuelle = list(db.patients.aggregate([
    {"$unwind": "$consultations"},
    {"$match": {
        "consultations.date": {"$gte": date_un_an}
    }},
    {"$group": {
        "_id": {
            "year": {"$year": "$consultations.date"},
            "month": {"$month": "$consultations.date"}
        },
        "count": {"$sum": 1}
    }},
    {"$sort": {"_id.year": 1, "_id.month": 1}},
    {"$project": {
        "_id": 0,
        "mois": {"$concat": [
            {"$toString": "$_id.year"}, "-", 
            {"$cond": [{"$lt": ["$_id.month", 10]}, {"$concat": ["0", {"$toString": "$_id.month"}]}, {"$toString": "$_id.month"}]}
        ]},
        "count": 1
    }}
]))
pprint(evolution_mensuelle)

print("\n=== 3.4 : Profil patients à risque élevé ===")
patients_risque = list(db.patients.aggregate([
    {"$match": {
        "antecedents": {"$all": ["Diabète type 2", "HTA"]}
    }},
    {"$addFields": {
        "age": {"$dateDiff": {"startDate": "$dateNaissance", "endDate": datetime.now(), "unit": "year"}},
        "nbConsultations": {"$size": {"$ifNull": ["$consultations", []]}}
    }},
    {"$match": {
        "age": {"$gt": 60}
    }},
    {"$group": {
        "_id": None,
        "totalPatients": {"$sum": 1},
        "moyenneConsultations": {"$avg": "$nbConsultations"}
    }}
]))
pprint(patients_risque)

print("\n=== 3.5 : Top 5 médecins & taux de ré-consultation ===")
rapport_medecins = list(db.patients.aggregate([
    {"$unwind": "$consultations"},
    {"$group": {
        "_id": "$consultations.medecin.nom",
        "totalConsultations": {"$sum": 1},
        "patientsUniques": {"$addToSet": "$_id"}
    }},
    {"$addFields": {
        "nbPatientsUniques": {"$size": "$patientsUniques"}
    }},
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
    {"$project": {"patientsUniques": 0}},
    {"$sort": {"totalConsultations": -1}},
    {"$limit": 5}
]))
pprint(rapport_medecins)
