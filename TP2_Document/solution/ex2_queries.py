import pymongo
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_db"]

print("=== 2.1 : Patients diabétiques de plus de 50 ans à Alger ===")
date_cinquante_ans = datetime.now() - relativedelta(years=50)

q2_1 = list(db.patients.find({
    "adresse.wilaya": "Alger",
    "antecedents": "Diabète type 2",
    "dateNaissance": {"$lt": date_cinquante_ans}
}))
pprint(q2_1)

print("\n=== 2.2 : Allergiques à la Pénicilline avec >= 3 consultations ===")
q2_2 = list(db.patients.find({
    "allergies": "Pénicilline",
    "consultations.2": {"$exists": True}
}))
pprint(q2_2)

print("\n=== 2.3 : Projection : Nom, prénom, dernière consultation ===")
q2_3 = list(db.patients.find(
    {},
    {"nom": 1, "prenom": 1, "consultations": {"$slice": -1}, "_id": 0}
).limit(5))
pprint(q2_3)

print("\n=== 2.4 : Sans antécédents, tension systolique > 140 (dernière consultation) ===")
q2_4 = list(db.patients.aggregate([
    {"$match": {"antecedents": {"$size": 0}}},
    {"$addFields": {"derniereConsultation": {"$arrayElemAt": ["$consultations", -1]}}},
    {"$match": {"derniereConsultation.tension.systolique": {"$gt": 140}}}
]))
pprint(q2_4)

print("\n=== 2.5 : Recherche textuelle sur les diagnostics ===")
# Create text index
db.patients.create_index([("consultations.diagnostic", pymongo.TEXT)])

q2_5 = list(db.patients.find(
    {"$text": {"$search": "Hypertension"}}
))
pprint(q2_5)
