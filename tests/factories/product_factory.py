def make_product_payload(category_id: int = 1) -> dict:
    return {
        "name": "Factory Product",
        "description": "Factory created product",
        "price": 99.99,
        "category_id": category_id,
    }
