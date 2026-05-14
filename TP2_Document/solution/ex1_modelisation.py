import pymongo
from datetime import datetime
import uuid

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_db"]

# Drop existing to start fresh
db.patients.drop()
db.analyses.drop()

# 1.1: Create collection with validation
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["cin", "nom", "prenom", "dateNaissance", "sexe"],
        "properties": {
            "cin": {"bsonType": "string", "description": "CIN obligatoire"},
            "nom": {"bsonType": "string", "description": "Nom obligatoire"},
            "prenom": {"bsonType": "string", "description": "Prénom obligatoire"},
            "dateNaissance": {"bsonType": "date", "description": "Date de naissance obligatoire"},
            "sexe": {"enum": ["M", "F"], "description": "Sexe doit être M ou F"},
            "adresse": {
                "bsonType": "object",
                "properties": {
                    "wilaya": {"bsonType": "string"},
                    "commune": {"bsonType": "string"}
                }
            },
            "groupeSanguin": {"enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]},
            "antecedents": {"bsonType": "array", "items": {"bsonType": "string"}},
            "allergies": {"bsonType": "array", "items": {"bsonType": "string"}},
            "consultations": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["id", "date", "medecin", "diagnostic"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "date": {"bsonType": "date"},
                        "medecin": {
                            "bsonType": "object",
                            "required": ["nom", "specialite"],
                            "properties": {
                                "nom": {"bsonType": "string"},
                                "specialite": {"bsonType": "string"}
                            }
                        },
                        "diagnostic": {"bsonType": "string"},
                        "tension": {
                            "bsonType": "object",
                            "properties": {
                                "systolique": {"bsonType": "int"},
                                "diastolique": {"bsonType": "int"}
                            }
                        },
                        "medicaments": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "properties": {
                                    "nom": {"bsonType": "string"},
                                    "dosage": {"bsonType": "string"},
                                    "duree": {"bsonType": "string"}
                                }
                            }
                        },
                        "notes": {"bsonType": "string"}
                    }
                }
            }
        }
    }
}

db.create_collection("patients", validator=validator)

# 1.2: Insert patients
patients = [
    {
        "cin": "198001012300",
        "nom": "Bensalem",
        "prenom": "Ahmed",
        "dateNaissance": datetime(1980, 1, 1),
        "sexe": "M",
        "adresse": {"wilaya": "Alger", "commune": "Bab Ezzouar"},
        "groupeSanguin": "O+",
        "antecedents": ["Diabète type 2", "HTA"],
        "allergies": ["Pénicilline"],
        "consultations": [
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 1, 15),
                "medecin": {"nom": "Dr. Mansouri", "specialite": "Cardiologie"},
                "diagnostic": "Hypertension artérielle",
                "tension": {"systolique": 145, "diastolique": 92},
                "medicaments": [
                    {"nom": "Amlodipine", "dosage": "5mg", "duree": "30 jours"}
                ],
                "notes": "Surveillance tensionnelle recommandée"
            },
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 3, 20),
                "medecin": {"nom": "Dr. Brahimi", "specialite": "Généraliste"},
                "diagnostic": "Grippe",
                "tension": {"systolique": 120, "diastolique": 80},
                "medicaments": [
                    {"nom": "Paracétamol", "dosage": "1g", "duree": "5 jours"}
                ],
                "notes": "Repos"
            }
        ]
    },
    {
        "cin": "199205051234",
        "nom": "Merzoug",
        "prenom": "Amina",
        "dateNaissance": datetime(1992, 5, 5),
        "sexe": "F",
        "adresse": {"wilaya": "Oran", "commune": "Sénia"},
        "groupeSanguin": "A+",
        "antecedents": ["Asthme"],
        "allergies": [],
        "consultations": [
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 2, 10),
                "medecin": {"nom": "Dr. Lamine", "specialite": "Pneumologie"},
                "diagnostic": "Crise d'asthme",
                "tension": {"systolique": 110, "diastolique": 70},
                "medicaments": [
                    {"nom": "Ventoline", "dosage": "100µg", "duree": "En cas de besoin"}
                ],
                "notes": "Suivi mensuel"
            }
        ]
    },
    {
        "cin": "197509124567",
        "nom": "Haddad",
        "prenom": "Karim",
        "dateNaissance": datetime(1975, 9, 12),
        "sexe": "M",
        "adresse": {"wilaya": "Constantine", "commune": "Khroub"},
        "groupeSanguin": "B+",
        "antecedents": ["Diabète type 2"],
        "allergies": ["Ibuprofène"],
        "consultations": [
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2023, 11, 5),
                "medecin": {"nom": "Dr. Yahi", "specialite": "Endocrinologie"},
                "diagnostic": "Diabète non équilibré",
                "tension": {"systolique": 130, "diastolique": 85},
                "medicaments": [
                    {"nom": "Metformine", "dosage": "850mg", "duree": "Continue"}
                ],
                "notes": "Régime strict"
            },
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 4, 18),
                "medecin": {"nom": "Dr. Yahi", "specialite": "Endocrinologie"},
                "diagnostic": "Diabète équilibré",
                "tension": {"systolique": 125, "diastolique": 80},
                "medicaments": [
                    {"nom": "Metformine", "dosage": "850mg", "duree": "Continue"}
                ],
                "notes": "Continuer traitement"
            }
        ]
    },
    {
        "cin": "198811225678",
        "nom": "Touati",
        "prenom": "Fatma",
        "dateNaissance": datetime(1988, 11, 22),
        "sexe": "F",
        "adresse": {"wilaya": "Alger", "commune": "Kouba"},
        "groupeSanguin": "O-",
        "antecedents": [],
        "allergies": ["Pénicilline"],
        "consultations": [
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 1, 5),
                "medecin": {"nom": "Dr. Kaddour", "specialite": "Généraliste"},
                "diagnostic": "Angine",
                "tension": {"systolique": 115, "diastolique": 75},
                "medicaments": [
                    {"nom": "Amoxicilline", "dosage": "1g", "duree": "7 jours"}
                ],
                "notes": "Attention allergie"
            },
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 2, 15),
                "medecin": {"nom": "Dr. Kaddour", "specialite": "Généraliste"},
                "diagnostic": "Fatigue",
                "tension": {"systolique": 105, "diastolique": 65},
                "medicaments": [
                    {"nom": "Vitamine C", "dosage": "500mg", "duree": "15 jours"}
                ],
                "notes": "Repos"
            },
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 5, 1),
                "medecin": {"nom": "Dr. Kaddour", "specialite": "Généraliste"},
                "diagnostic": "Migraine",
                "tension": {"systolique": 120, "diastolique": 80},
                "medicaments": [
                    {"nom": "Paracétamol", "dosage": "1g", "duree": "3 jours"}
                ],
                "notes": "Boire beaucoup d'eau"
            }
        ]
    },
    {
        "cin": "196503148901",
        "nom": "Belkacem",
        "prenom": "Mohamed",
        "dateNaissance": datetime(1965, 3, 14),
        "sexe": "M",
        "adresse": {"wilaya": "Blida", "commune": "Boufarik"},
        "groupeSanguin": "AB+",
        "antecedents": ["HTA", "Diabète type 2"],
        "allergies": [],
        "consultations": [
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, 5, 10),
                "medecin": {"nom": "Dr. Mansouri", "specialite": "Cardiologie"},
                "diagnostic": "Hypertension artérielle sévère",
                "tension": {"systolique": 160, "diastolique": 95},
                "medicaments": [
                    {"nom": "Loxen", "dosage": "50mg", "duree": "Continue"}
                ],
                "notes": "Risque cardiovasculaire"
            }
        ]
    }
]

# Add more to reach 20
wilayas = ["Alger", "Oran", "Constantine", "Annaba", "Blida", "Tizi Ouzou", "Sétif", "Batna"]
prenomsH = ["Ali", "Omar", "Yacine", "Amine", "Walid", "Riad", "Samir"]
prenomsF = ["Sarah", "Imène", "Nadia", "Mounia", "Leila", "Zahra", "Sonia"]
noms = ["Boudiaf", "Saidi", "Derradji", "Hamid", "Ghezali", "Cherif", "Ziani"]

for i in range(6, 21):
    isMale = (i % 2 != 0)
    prenom = prenomsH[i % len(prenomsH)] if isMale else prenomsF[i % len(prenomsF)]
    patients.append({
        "cin": f"19{80+i}0{(i%9)+1}10{1000+i}",
        "nom": noms[i % len(noms)],
        "prenom": prenom,
        "dateNaissance": datetime(1980+i, (i%9)+1, 10),
        "sexe": "M" if isMale else "F",
        "adresse": {"wilaya": wilayas[i % len(wilayas)], "commune": "Centre"},
        "groupeSanguin": "O+",
        "antecedents": ["Diabète type 2"] if i % 4 == 0 else [],
        "allergies": [],
        "consultations": [
            {
                "id": str(uuid.uuid4()),
                "date": datetime(2024, (i%5)+1, 10),
                "medecin": {"nom": "Dr. Test", "specialite": "Généraliste"},
                "diagnostic": "Hypertension artérielle" if i % 2 == 0 else "Routine",
                "tension": {"systolique": 120, "diastolique": 80},
                "medicaments": [],
                "notes": "RAS"
            }
        ]
    })

db.patients.insert_many(patients)

# 1.3 Analyses
patients_inseres = list(db.patients.find().limit(5))
analyses = []

if len(patients_inseres) > 0:
    analyses.append({
        "patient_id": patients_inseres[0]["_id"],
        "date": datetime(2024, 1, 20),
        "type": "Glycémie",
        "resultats": {"valeur": 1.45, "unite": "g/L"},
        "laboratoire": "Labo Central Alger",
        "valide": True
    })
    
    analyses.append({
        "patient_id": patients_inseres[2]["_id"],
        "date": datetime(2023, 11, 10),
        "type": "Glycémie",
        "resultats": {"valeur": 1.10, "unite": "g/L"},
        "laboratoire": "Labo Pasteur",
        "valide": True
    })
    
    analyses.append({
        "patient_id": patients_inseres[4]["_id"],
        "date": datetime(2018, 5, 10),
        "type": "Lipidogramme",
        "resultats": {"cholesterol": 2.5},
        "laboratoire": "Labo Blida",
        "valide": True
    })

db.analyses.insert_many(analyses)

print(f" Modélisation terminée. Patients insérés: {db.patients.count_documents({})}")
print(f" Analyses insérées: {db.analyses.count_documents({})}")
