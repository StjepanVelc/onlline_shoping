from typing import List, Tuple


class Order:
    def __init__(self, id: int, user_id: int, address: str):
        
        if not isinstance(id, int) or id <= 0:
            raise ValueError("Order ID must be a positive integer.")

        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer.")

        if not address or len(address.strip()) < 5:
            raise ValueError("Order must have a valid delivery address.")

        self.id = id
        self.user_id = user_id
        self.address = address

        # --- STANJE ORDERA ---
        self.status = "CREATED"

        # --- STAVKE ORDERA ---
        # Svaka stavka je (product, quantity)
        self.items: List[Tuple[object, int]] = []

    # -------------------------
    # RAD SA PROIZVODIMA
    # -------------------------

    def add_product(self, product, quantity: int) -> None:
        if self.status != "CREATED":
            raise ValueError("Cannot add products after order is confirmed.")

        if quantity <= 0:
            raise ValueError("Quantity must be a positive number.")

        self.items.append((product, quantity))

    def remove_product(self, product) -> None:
        if self.status != "CREATED":
            raise ValueError("Cannot remove products after order is confirmed.")

        self.items = [(p, q) for (p, q) in self.items if p != product]

    def has_products(self) -> bool:
        return len(self.items) > 0

    # -------------------------
    # ADRESA
    # -------------------------

    def update_address(self, new_address: str) -> None:
        if self.status != "CREATED":
            raise ValueError("Cannot change address after order is confirmed.")

        if not new_address or len(new_address.strip()) < 5:
            raise ValueError("Invalid address.")

        self.address = new_address

    # -------------------------
    # STATUS ORDERA
    # -------------------------

    def confirm(self) -> None:
        if not self.items:
            raise ValueError("Order must contain at least one product.")

        self.status = "CONFIRMED"

    def cancel(self) -> None:
        if self.status == "SHIPPED":
            raise ValueError("Cannot cancel a shipped order.")

        self.status = "CANCELLED"

    # -------------------------
    # INFO / DISPLAY
    # -------------------------

    def total_items(self) -> int:
        return sum(quantity for _, quantity in self.items)

    def display_order_info(self) -> str:
        return (
            f"Order ID: {self.id}, "
            f"User ID: {self.user_id}, "
            f"Status: {self.status}, "
            f"Address: {self.address}, "
            f"Items: {self.total_items()}"
        )
