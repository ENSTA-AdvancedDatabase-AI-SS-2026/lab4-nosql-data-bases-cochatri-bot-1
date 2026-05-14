"""
TP1 - Exercice 4 : Classement des meilleures ventes
Use Case : Top produits ShopFast en temps réel
"""
import redis
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

LEADERBOARD_KEY = "leaderboard:sales"


def record_sale(r, product_id, quantity: int = 1):
    """
    Enregistrer une vente dans le classement
    Utiliser ZINCRBY sur la clé LEADERBOARD_KEY
    """
    r.zincrby(LEADERBOARD_KEY, quantity, product_id)


def get_top_products(r, n: int = 10) -> list:
    """
    Retourner les N produits les plus vendus
    Format : [{"product_id": "1", "sales": 150}, ...]
    """
    results = r.zrevrange(LEADERBOARD_KEY, 0, n - 1, withscores=True)
    return [{"product_id": pid, "sales": int(score)} for pid, score in results]


def get_product_rank(r, product_id) -> Optional[int]:
    """
    Retourner le rang 1-based d'un produit
    """
    rank = r.zrevrank(LEADERBOARD_KEY, product_id)
    if rank is None:
        return None
    return rank + 1  # convert 0-based → 1-based


def get_products_between_ranks(r, start_rank: int, end_rank: int) -> list:
    """
    Retourner les produits entre les rangs start et end (1-based)
    """
    start = start_rank - 1
    end = end_rank - 1

    results = r.zrevrange(LEADERBOARD_KEY, start, end, withscores=True)
    return [{"product_id": pid, "sales": int(score)} for pid, score in results]


def simulate_sales_day(r, n_sales: int = 500):
    """
    Simuler une journée de ventes aléatoires
    """
    import random
    products = list(range(1, 21))

    for _ in range(n_sales):
        product_id = random.choice(products)
        qty = random.randint(1, 5)
        record_sale(r, product_id, qty)


if __name__ == "__main__":
    r.flushdb()

    print("Simulation de ventes...")
    simulate_sales_day(r, 500)

    print("\n🏆 Top 5 produits:")
    for i, p in enumerate(get_top_products(r, 5), 1):
        print(f"  {i}. Produit #{p['product_id']} — {p['sales']} ventes")

    print(f"\nRang du produit #1: {get_product_rank(r, 1)}")
