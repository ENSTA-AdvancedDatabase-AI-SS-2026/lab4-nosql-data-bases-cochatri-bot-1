/**
 * TP2 - Exercice 1 : Modélisation MongoDB
 * Use Case : HealthCare DZ - Dossiers Médicaux
 */

use("medical_db");

// ─── 1.1 : Collection avec validation ────────────────────────────────
db.createCollection("patients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cin", "nom", "prenom", "dateNaissance", "sexe", "adresse"],
      properties: {
        cin: { bsonType: "string", description: "CIN obligatoire" },
        nom: { bsonType: "string" },
        prenom: { bsonType: "string" },
        dateNaissance: { bsonType: "date" },
        sexe: { bsonType: "string", enum: ["M", "F"] },

        adresse: {
          bsonType: "object",
          required: ["wilaya", "commune"],
          properties: {
            wilaya: { bsonType: "string" },
            commune: { bsonType: "string" }
          }
        },

        groupeSanguin: {
          bsonType: "string",
          enum: ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        },

        antecedents: {
          bsonType: "array",
          items: { bsonType: "string" }
        },

        allergies: {
          bsonType: "array",
          items: { bsonType: "string" }
        },

        consultations: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["id", "date", "medecin", "diagnostic"],
            properties: {
              id: { bsonType: "binData" },
              date: { bsonType: "date" },
              medecin: {
                bsonType: "object",
                required: ["nom", "specialite"],
                properties: {
                  nom: { bsonType: "string" },
                  specialite: { bsonType: "string" }
                }
              },
              diagnostic: { bsonType: "string" },
              tension: {
                bsonType: "object",
                properties: {
                  systolique: { bsonType: "int" },
                  diastolique: { bsonType: "int" }
                }
              },
              medicaments: {
                bsonType: "array",
                items: {
                  bsonType: "object",
                  properties: {
                    nom: { bsonType: "string" },
                    dosage: { bsonType: "string" },
                    duree: { bsonType: "string" }
                  }
                }
              },
              notes: { bsonType: "string" }
            }
          }
        }
      }
    }
  }
});

// ─── 1.2 : Patients (20 patients) ────────────────────────────────

const patients = [
  {
    cin: "198001012300",
    nom: "Bensalem",
    prenom: "Ahmed",
    dateNaissance: new Date("1980-01-01"),
    sexe: "M",
    adresse: { wilaya: "Alger", commune: "Bab Ezzouar" },
    groupeSanguin: "O+",
    antecedents: ["Diabète type 2", "HTA"],
    allergies: ["Pénicilline"],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-01-15"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: "Hypertension artérielle",
        tension: { systolique: 145, diastolique: 92 },
        medicaments: [{ nom: "Amlodipine", dosage: "5mg", duree: "30 jours" }],
        notes: "Surveillance tensionnelle"
      }
    ]
  },

  {
    cin: "199205142301",
    nom: "Khelifi",
    prenom: "Sara",
    dateNaissance: new Date("1992-05-14"),
    sexe: "F",
    adresse: { wilaya: "Oran", commune: "Bir El Djir" },
    groupeSanguin: "A+",
    antecedents: ["Asthme"],
    allergies: [],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-02-10"),
        medecin: { nom: "Dr. Yacine", specialite: "Pneumologie" },
        diagnostic: "Crise d’asthme",
        medicaments: [{ nom: "Ventoline", dosage: "100mcg", duree: "14 jours" }],
        notes: "Amélioration après traitement"
      }
    ]
  },

  {
    cin: "197510082302",
    nom: "Benali",
    prenom: "Mohamed",
    dateNaissance: new Date("1975-10-08"),
    sexe: "M",
    adresse: { wilaya: "Constantine", commune: "El Khroub" },
    groupeSanguin: "B+",
    antecedents: ["HTA"],
    allergies: [],
    consultations: [
      {
        id: UUID(),
        date: new Date("2023-11-20"),
        medecin: { nom: "Dr. Haddad", specialite: "Médecine générale" },
        diagnostic: "Contrôle HTA",
        tension: { systolique: 140, diastolique: 88 },
        medicaments: [{ nom: "Losartan", dosage: "50mg", duree: "60 jours" }],
        notes: "Bonne évolution"
      }
    ]
  },

  {
    cin: "200110122303",
    nom: "Zerrouki",
    prenom: "Yasmine",
    dateNaissance: new Date("2001-10-12"),
    sexe: "F",
    adresse: { wilaya: "Blida", commune: "Boufarik" },
    groupeSanguin: "O-",
    antecedents: [],
    allergies: ["Pollen"],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-03-05"),
        medecin: { nom: "Dr. Saidi", specialite: "Allergologie" },
        diagnostic: "Rhinite allergique",
        medicaments: [{ nom: "Antihistaminique", dosage: "10mg", duree: "10 jours" }],
        notes: "Éviter exposition pollen"
      }
    ]
  }
];

// Fill remaining patients automatically (to reach 20)
const wilayas = ["Alger", "Oran", "Constantine", "Annaba", "Blida"];
const noms = ["Boudjemaa", "Cherif", "Meziane", "Djebbar", "Larbi", "Fares", "Hamidi", "Sahraoui", "Belaid", "Guerfi"];
const prenoms = ["Ali", "Nadia", "Omar", "Lina", "Karim", "Imane", "Yacine", "Rania", "Samir", "Aya"];

for (let i = 0; patients.length < 20; i++) {
  patients.push({
    cin: `1990000${i}30${i}`,
    nom: noms[i % noms.length],
    prenom: prenoms[i % prenoms.length],
    dateNaissance: new Date(1985, i % 12, (i % 28) + 1),
    sexe: i % 2 === 0 ? "M" : "F",
    adresse: {
      wilaya: wilayas[i % wilayas.length],
      commune: "Centre"
    },
    groupeSanguin: "O+",
    antecedents: i % 3 === 0 ? ["Diabète"] : [],
    allergies: [],
    consultations: [
      {
        id: UUID(),
        date: new Date(2024, i % 12, (i % 28) + 1),
        medecin: { nom: "Dr. Central", specialite: "Généraliste" },
        diagnostic: "Consultation de routine",
        notes: "RAS"
      }
    ]
  });
}

db.patients.insertMany(patients);

// ─── 1.3 : Analyses ────────────────────────────────

const analyses = [];

patients.forEach(p => {
  analyses.push(
    {
      patient_id: p.cin,
      type: "Glycémie",
      result: Math.floor(Math.random() * 2) + 1.0,
      date: new Date()
    },
    {
      patient_id: p.cin,
      type: "NFS",
      result: "Normal",
      date: new Date()
    },
    {
      patient_id: p.cin,
      type: "ECG",
      result: "Normal sinus rhythm",
      date: new Date()
    }
  );
});

db.analyses.insertMany(analyses);

// ─── RESULT ────────────────────────────────

print("✅ Modélisation terminée. Patients insérés:", db.patients.countDocuments());
print("✅ Analyses insérées:", db.analyses.countDocuments());

// ─── 1.2 : Insérer des patients avec données algériennes ──────────────────────
// TODO: Insérer au moins 20 patients avec :
// - Prénoms et noms algériens variés
// - Wilayas différentes (Alger, Oran, Constantine, Annaba, Blida...)
// - Pathologies courantes (Diabète, HTA, Asthme, etc.)
// - Au moins 2-5 consultations par patient
// - Dates réalistes sur les 2 dernières années

const patients = [
  {
    cin: "198001012300",
    nom: "Bensalem",
    prenom: "Ahmed",
    dateNaissance: new Date("1980-01-01"),
    sexe: "M",
    adresse: { wilaya: "Alger", commune: "Bab Ezzouar" },
    groupeSanguin: "O+",
    antecedents: ["Diabète type 2", "HTA"],
    allergies: ["Pénicilline"],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-01-15"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: "Hypertension artérielle",
        tension: { systolique: 145, diastolique: 92 },
        medicaments: [
          { nom: "Amlodipine", dosage: "5mg", duree: "30 jours" }
        ],
        notes: "Surveillance tensionnelle recommandée"
      }
      // TODO: Ajouter d'autres consultations
    ]
  },
  // TODO: Ajouter 19 autres patients
];

// db.patients.insertMany(patients);

// ─── 1.3 : Collection analyses (référencée) ───────────────────────────────────
// TODO: Créer des analyses pour les patients insérés
// Types : "Glycémie", "NFS", "Lipidogramme", "Créatinine", "ECG"

const analyses = [
  // TODO: Insérer des analyses avec patient_id référençant les patients
];

// db.analyses.insertMany(analyses);

print("✅ Modélisation terminée. Patients insérés:", db.patients.countDocuments());
print("✅ Analyses insérées:", db.analyses.countDocuments());
