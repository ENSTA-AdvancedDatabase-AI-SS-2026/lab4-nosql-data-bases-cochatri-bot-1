"""
TP1 - Exercice 3 : Pattern Cache-Aside avec TTL
Use Case : Cache des pages produits ShopFast
"""
import redis
import json
import time
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def slow_db_get_product(product_id: int) -> Optional[dict]:
    """Simule une requête PostgreSQL lente (2 secondes)"""
    time.sleep(2)
    products = {
        1: {"id": 1, "name": "Samsung Galaxy A54", "price": 65000, "stock": 15},
        2: {"id": 2, "name": "Laptop HP 15-inch", "price": 120000, "stock": 8},
        3: {"id": 3, "name": "Casque JBL Bluetooth", "price": 12000, "stock": 50},
        4: {"id": 4, "name": "Clavier Mécanique", "price": 8000, "stock": 30},
    }
    return products.get(product_id)


def get_product_cached(r, product_id: int, ttl: int = 600) -> Optional[dict]:
    """
    Cache-Aside:
    - Redis first
    - fallback DB
    - store with TTL
    """
    start = time.time()
    key = f"product_cache:{product_id}"

    # 1. CHECK CACHE
    cached = r.get(key)

    if cached:
        product = json.loads(cached)
        elapsed = (time.time() - start) * 1000
        print(f"CACHE HIT ({elapsed:.2f}ms)")
        return product

    # 2. CACHE MISS → DB
    product = slow_db_get_product(product_id)

    if product is None:
        elapsed = (time.time() - start) * 1000
        print(f"CACHE MISS (not found) ({elapsed:.2f}ms)")
        return None

    # 3. STORE IN CACHE
    r.setex(key, ttl, json.dumps(product))

    elapsed = (time.time() - start) * 1000
    print(f"CACHE MISS ({elapsed:.2f}ms)")
    return product


def invalidate_product_cache(r, product_id: int):
    """Supprimer le cache d'un produit (après mise à jour en DB)"""
    key = f"product_cache:{product_id}"
    r.delete(key)


def benchmark_cache(r, product_id: int, iterations: int = 20):
    """
    Compare cache HIT vs MISS performance
    """
    hit_times = []
    miss_times = []
    hits = 0

    # clear cache first for clean benchmark
    invalidate_product_cache(r, product_id)

    for i in range(iterations):
        start = time.time()
        key = f"product_cache:{product_id}"

        cached = r.get(key)

        if cached:
            json.loads(cached)
            elapsed = (time.time() - start) * 1000
            hit_times.append(elapsed)
            hits += 1
        else:
            slow_db_get_product(product_id)
            product = slow_db_get_product(product_id)
            r.setex(key, 600, json.dumps(product))
            elapsed = (time.time() - start) * 1000
            miss_times.append(elapsed)

    hit_rate = (hits / iterations) * 100

    avg_hit = sum(hit_times) / len(hit_times) if hit_times else 0
    avg_miss = sum(miss_times) / len(miss_times) if miss_times else 0

    print("\n=== Benchmark Results ===")
    print(f"Avg CACHE HIT: {avg_hit:.2f}ms")
    print(f"Avg CACHE MISS: {avg_miss:.2f}ms")
    print(f"Hit rate: {hit_rate:.1f}%")


if __name__ == "__main__":
    r.flushdb()

    print("=== Test Cache-Aside ===")
    print("\nPremier appel (MISS attendu):")
    get_product_cached(r, 1)

    print("\nDeuxième appel (HIT attendu):")
    get_product_cached(r, 1)

    print("\n=== Benchmark ===")
    benchmark_cache(r, 1, iterations=10)
