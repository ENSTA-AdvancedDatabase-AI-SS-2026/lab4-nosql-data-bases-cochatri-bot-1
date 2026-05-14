"""
TP3 - Exercice 2 : Ingestion de données IoT
Use Case : SmartGrid DZ
"""
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
import uuid
import random
from datetime import datetime, timedelta
import time

# Configuration
CASSANDRA_HOST = 'localhost'
KEYSPACE = 'smartgrid'
NB_CAPTEURS = 1000  # Réduit pour les tests locaux (initialement 10000)
MINUTES_HISTORIQUE = 5

WILAYAS = ["Alger", "Oran", "Constantine", "Annaba", "Blida"]
COMMUNES = {
    "Alger": ["Bab Ezzouar", "Hydra", "El Harrach", "Dar El Beida"],
    "Oran": ["Bir El Djir", "Es Senia", "Arzew"],
    "Constantine": ["El Khroub", "Ain Smara", "Hamma Bouziane"],
    "Annaba": ["El Bouni", "El Hadjar", "Seraidi"],
    "Blida": ["Bougara", "Boufarik", "Larbaa"],
}

def connect():
    """Connexion au cluster Cassandra"""
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect(KEYSPACE)
    return session, cluster


def generate_mesure(capteur_id, wilaya, commune, timestamp):
    """Générer une mesure réaliste pour un capteur"""
    tension_base = 220  # Volts (réseau algérien)
    
    return {
        "capteur_id": capteur_id,
        "date_jour": timestamp.strftime('%Y-%m-%d'),
        "timestamp": timestamp,
        "wilaya": wilaya,
        "commune": commune,
        "tension_v": round(tension_base + random.gauss(0, 5), 2),
        "courant_a": round(random.uniform(0.5, 15.0), 2),
        "puissance_kw": round(random.uniform(0.1, 3.3), 3),
        "frequence_hz": round(50 + random.gauss(0, 0.1), 2),
        "temperature": round(random.uniform(20, 65), 1),
        "alerte": random.random() < 0.05,
    }


def run_ingestion(session):
    print(f"Démarrage ingestion : {NB_CAPTEURS} capteurs × {MINUTES_HISTORIQUE} min")
    
    # 2.1 / 2.2 Préparer les requêtes
    insert_mesure_stmt = session.prepare("""
        INSERT INTO mesures_par_capteur 
        (capteur_id, date_jour, timestamp, wilaya, commune, tension_v, courant_a, puissance_kw, frequence_hz, temperature, alerte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        USING TTL 7776000
    """)
    
    insert_alerte_stmt = session.prepare("""
        INSERT INTO alertes_par_wilaya
        (wilaya, date_jour, timestamp, capteur_id, code_alerte, description, gravite, resolue)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        USING TTL 31536000
    """)

    # Génération des capteurs
    capteurs = []
    for _ in range(NB_CAPTEURS):
        w = random.choice(WILAYAS)
        c = random.choice(COMMUNES[w])
        capteurs.append((uuid.uuid4(), w, c))

    start_time = datetime.now() - timedelta(minutes=MINUTES_HISTORIQUE)
    global_start = time.time()
    
    total_mesures = 0
    total_alertes = 0

    for minute in range(MINUTES_HISTORIQUE):
        current_time = start_time + timedelta(minutes=minute)
        
        batch_mesures = BatchStatement(batch_type=BatchType.UNLOGGED)
        batch_alertes = BatchStatement(batch_type=BatchType.UNLOGGED)
        
        for i, (cid, w, c) in enumerate(capteurs):
            m = generate_mesure(cid, w, c, current_time)
            
            batch_mesures.add(insert_mesure_stmt, (
                m["capteur_id"], m["date_jour"], m["timestamp"], 
                m["wilaya"], m["commune"], m["tension_v"], 
                m["courant_a"], m["puissance_kw"], m["frequence_hz"], 
                m["temperature"], m["alerte"]
            ))
            total_mesures += 1
            
            if m["alerte"]:
                batch_alertes.add(insert_alerte_stmt, (
                    m["wilaya"], m["date_jour"], m["timestamp"],
                    m["capteur_id"], "ALERTE_TENSION", "Fluctuation détectée", 2, False
                ))
                total_alertes += 1
                
            # Exécuter les batchs toutes les 50 requêtes pour éviter de surcharger
            if (i + 1) % 50 == 0:
                session.execute(batch_mesures)
                if len(batch_alertes) > 0:
                    session.execute(batch_alertes)
                batch_mesures.clear()
                batch_alertes.clear()
                
        # Exécuter les requêtes restantes
        if len(batch_mesures) > 0:
            session.execute(batch_mesures)
        if len(batch_alertes) > 0:
            session.execute(batch_alertes)

    elapsed = time.time() - global_start
    print(f"\n {total_mesures:,} mesures insérées en {elapsed:.1f}s")
    print(f" {total_alertes:,} alertes insérées")
    print(f"   Débit : {total_mesures/elapsed:,.0f} mesures/seconde")


if __name__ == "__main__":
    session, cluster = connect()
    run_ingestion(session)
    cluster.shutdown()
