def test_order_creation_list_and_details(client):
    user_response = client.post(
        "/users",
        json={
            "username": "marko",
            "email": "marko@example.com",
            "country": "HR",
        },
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Laptop X",
            "description": "Test product",
            "price": 1000.0,
            "stock": 5,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    order_response = client.post(
        "/orders",
        json={
            "user_id": user_id,
            "address": "Ilica 1, Zagreb",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
        },
    )
    assert order_response.status_code == 201
    order = order_response.json()
    assert order["total_amount"] == 2000.0

    orders_list_response = client.get("/orders")
    assert orders_list_response.status_code == 200
    orders = orders_list_response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == order["id"]

    order_details_response = client.get(f"/orders/{order['id']}")
    assert order_details_response.status_code == 200
    order_details = order_details_response.json()
    assert len(order_details["items"]) == 1
    assert order_details["items"][0]["quantity"] == 2

    updated_product_response = client.get(f"/products/{product_id}")
    assert updated_product_response.status_code == 200
    assert updated_product_response.json()["stock"] == 3


def test_order_creation_with_insufficient_stock_returns_400(client):
    user_response = client.post(
        "/users",
        json={
            "username": "ana",
            "email": "ana@example.com",
            "country": "HR",
        },
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "Mouse Z",
            "description": "Gaming mouse",
            "price": 50.0,
            "stock": 1,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    bad_order_response = client.post(
        "/orders",
        json={
            "user_id": user_id,
            "address": "Savska 12, Zagreb",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
        },
    )
    assert bad_order_response.status_code == 400

    product_after_failed_order = client.get(f"/products/{product_id}")
    assert product_after_failed_order.status_code == 200
    assert product_after_failed_order.json()["stock"] == 1


def test_get_missing_order_details_returns_404(client):
    missing_order_response = client.get("/orders/9999")
    assert missing_order_response.status_code == 404
