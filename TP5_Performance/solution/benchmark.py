"""
TP5 - Benchmark Comparatif NoSQL
Mesurer les performances de Redis, MongoDB, Cassandra, Neo4j
"""
import time
import statistics
import json
import threading
from typing import Callable, List, Tuple
import redis
from pymongo import MongoClient
from pymongo import InsertOne
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
import uuid

# ─── Utilitaires de mesure ────────────────────────────────────────────────────

def measure_execution_time(name: str, fn: Callable):
    start = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - start
    print(f"[{name}] Temps d'exécution : {elapsed:.2f}s")
    return elapsed

# ─── Ex1 : Benchmark Écriture ─────────────────────────────────────────────────

def benchmark_write_redis(n: int = 100_000):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.flushdb()
    
    def write_task():
        # Utiliser un pipeline pour maximiser le débit (envoi par lots)
        pipeline = r.pipeline(transaction=False)
        for i in range(n):
            pipeline.set(f"user:{i}", f"data_{i}")
            if i > 0 and i % 10000 == 0:
                pipeline.execute()
        pipeline.execute()

    elapsed = measure_execution_time("Redis Write", write_task)
    print(f"  -> Débit : {n/elapsed:,.0f} requêtes/seconde")


def benchmark_write_mongodb(n: int = 100_000):
    client = MongoClient("mongodb://admin:admin123@localhost:27017/")
    db = client["benchmark"]
    collection = db["users"]
    collection.drop()

    def write_task():
        # Utiliser bulk_write pour envoyer les données en gros paquets
        batch = []
        for i in range(n):
            batch.append(InsertOne({"_id": i, "name": f"user_{i}", "data": f"data_{i}"}))
            if len(batch) == 10000:
                collection.bulk_write(batch, ordered=False)
                batch = []
        if batch:
            collection.bulk_write(batch, ordered=False)

    elapsed = measure_execution_time("MongoDB Write", write_task)
    print(f"  -> Débit : {n/elapsed:,.0f} requêtes/seconde")


def benchmark_write_cassandra(n: int = 100_000):
    # Setup
    cluster = Cluster(['localhost'])
    try:
        session = cluster.connect()
        session.execute("CREATE KEYSPACE IF NOT EXISTS benchmark WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
        session.set_keyspace('benchmark')
        session.execute("CREATE TABLE IF NOT EXISTS users (id int PRIMARY KEY, name text, data text)")
        session.execute("TRUNCATE users")
        
        insert_stmt = session.prepare("INSERT INTO users (id, name, data) VALUES (?, ?, ?)")

        def write_task():
            # Utilisation de BatchStatement non loggés (taille 100 max en Cassandra)
            batch = BatchStatement(batch_type=BatchType.UNLOGGED)
            for i in range(n):
                batch.add(insert_stmt, (i, f"user_{i}", f"data_{i}"))
                if i > 0 and i % 100 == 0:
                    session.execute(batch)
                    batch.clear()
            if len(batch) > 0:
                session.execute(batch)

        elapsed = measure_execution_time("Cassandra Write", write_task)
        print(f"  -> Débit : {n/elapsed:,.0f} requêtes/seconde")
    except Exception as e:
        print(f"Cassandra Write Error: {e}")
    finally:
        cluster.shutdown()

# ─── Ex2 : Benchmark Lecture ─────────────────────────────────────────────────

def benchmark_read_redis(n_reads: int = 10000):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def read_task():
        # Point lookups séquentiels pour simuler une charge applicative
        for i in range(n_reads):
            r.get(f"user:{i}")

    elapsed = measure_execution_time("Redis Read (Point Lookup)", read_task)
    print(f"  -> Débit : {n_reads/elapsed:,.0f} requêtes/seconde")


def benchmark_read_mongodb(n_reads: int = 10000):
    client = MongoClient("mongodb://admin:admin123@localhost:27017/")
    collection = client["benchmark"]["users"]

    def read_task():
        # Point lookups séquentiels
        for i in range(n_reads):
            collection.find_one({"_id": i})

    elapsed = measure_execution_time("MongoDB Read (Point Lookup)", read_task)
    print(f"  -> Débit : {n_reads/elapsed:,.0f} requêtes/seconde")

# ─── Ex3 : Charge concurrente ─────────────────────────────────────────────────

def benchmark_concurrent(db_name: str, fn: Callable, n_clients: int = 50):
    threads = []
    
    start = time.perf_counter()
    for _ in range(n_clients):
        t = threading.Thread(target=fn)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    elapsed = time.perf_counter() - start
    print(f"[{db_name} Concurrent] {n_clients} clients. Temps total : {elapsed:.2f}s")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Benchmark NoSQL - Comparatif des technologies")
    print("="*60)
    
    N = 100_000  # Enregistrements
    N_READS = 10_000
    
    print(f"\n📝 Benchmark Écriture ({N:,} enregistrements)")
    benchmark_write_redis(N)
    benchmark_write_mongodb(N)
    benchmark_write_cassandra(N)
    
    print(f"\n📖 Benchmark Lecture ({N_READS:,} requêtes)")
    benchmark_read_redis(N_READS)
    benchmark_read_mongodb(N_READS)
    
    print(f"\n⚡ Test Charge Concurrente (50 clients, lectures)")
    def redis_read_worker():
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        for i in range(200):
            r.get(f"user:{i}")
            
    def mongo_read_worker():
        client = MongoClient("mongodb://admin:admin123@localhost:27017/")
        collection = client["benchmark"]["users"]
        for i in range(200):
            collection.find_one({"_id": i})
            
    benchmark_concurrent("Redis", redis_read_worker, n_clients=50)
    benchmark_concurrent("MongoDB", mongo_read_worker, n_clients=50)
    
    print("\n✅ Benchmark terminé ! Consultez RAPPORT.md pour l'analyse.")
