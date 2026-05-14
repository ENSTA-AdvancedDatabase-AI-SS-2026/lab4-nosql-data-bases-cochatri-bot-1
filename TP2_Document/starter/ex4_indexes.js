use("medical_db");

// ─── 4.1 : INDEX CREATION ────────────────────────────────────────

print("=== Creating indexes ===");

// Index 1 : wilaya + antecedents (frequent filtering)
db.patients.createIndex({
  "adresse.wilaya": 1,
  antecedents: 1
});

// Index 2 : consultation date (nested field)
db.patients.createIndex({
  "consultations.date": 1
});

// Index 3 : Full-text search on diagnosis
db.patients.createIndex({
  "consultations.diagnostic": "text"
});

// Index 4 : Analyses lookup by patient
db.analyses.createIndex({
  patient_id: 1
});

print("✅ Indexes created");


// ─── 4.2 : explain() comparison ────────────────────────────────────────

const requeteTest = {
  "adresse.wilaya": "Alger",
  antecedents: "Diabète type 2"
};

print("=== AVANT index (run explain) ===");

printjson(
  db.patients.find(requeteTest).explain("executionStats")
);

// After indexes (run same query again)
print("\n=== APRÈS index (run explain) ===");

printjson(
  db.patients.find(requeteTest).explain("executionStats")
);


// ─── 4.4 : TTL INDEX ────────────────────────────────────────

print("=== Creating TTL index ===");

// 5 years = 5 * 365 * 24 * 60 * 60 seconds
db.analyses.createIndex(
  { date: 1 },
  { expireAfterSeconds: 157680000 }
);

print(" TTL index created (5 years expiration)");
