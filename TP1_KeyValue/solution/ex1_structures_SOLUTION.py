import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def store_product(product_id, product_data: dict):
    r.hset(f"product:{product_id}", mapping=product_data)

def get_product(product_id):
    data = r.hgetall(f"product:{product_id}")
    return data if data else None

def add_to_cart(user_id, product_id, quantity=1):
    r.hincrby(f"cart:{user_id}", str(product_id), quantity)

def get_cart(user_id):
    return r.hgetall(f"cart:{user_id}")

def record_view(user_id, product_id, max_history=10):
    key = f"history:{user_id}"
    r.lpush(key, str(product_id))
    r.ltrim(key, 0, max_history - 1)

def get_history(user_id):
    return r.lrange(f"history:{user_id}", 0, -1)

def add_product_to_category(category, product_id):
    r.sadd(f"category:{category}", str(product_id))

def get_products_in_categories(*categories):
    keys = [f"category:{cat}" for cat in categories]
    return r.sinter(*keys)

if __name__ == "__main__":
    store_product("1", {"name": "Laptop", "price": "1500"})
    print(get_product("1"))

    add_to_cart("user1", "1", 2)
    print(get_cart("user1"))

    record_view("user1", "1")
    record_view("user1", "2")
    print(get_history("user1"))

    add_product_to_category("electronics", "1")
    add_product_to_category("electronics", "2")
    add_product_to_category("laptops", "1")

    print(get_products_in_categories("electronics", "laptops")) 
