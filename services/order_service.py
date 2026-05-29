import sqlite3
from typing import Dict, List, Optional

from repositories.order_repo import OrderRepository
from repositories.product_repo import ProductRepository
from repositories.user_repo import UserRepository
from services.exceptions import NotFoundError, ValidationError


class OrderService:
    def __init__(
        self,
        *,
        order_repo: OrderRepository,
        user_repo: UserRepository,
        product_repo: ProductRepository,
        db,
    ):
        self.order_repo = order_repo
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.db = db

    def create_order(self, payload) -> Dict:
        if not payload.items:
            raise ValidationError("Order must have at least one item")

        user = self.user_repo.get_user_by_id(payload.user_id)
        if not user:
            raise NotFoundError("User not found")

        # One transaction for order header, items and stock updates.
        try:
            self.db.execute("BEGIN")
            order_id = self.order_repo.create_order(
                user_id=payload.user_id,
                address=payload.address,
                status="pending",
            )

            total = 0.0
            for item in payload.items:
                product = self.product_repo.get_product_by_id(item.product_id)
                if not product:
                    raise ValidationError(
                        f"Product {item.product_id} does not exist"
                    )
                if product["stock"] < item.quantity:
                    raise ValidationError(
                        f"Not enough stock for product {item.product_id}"
                    )

                price = float(product["price"])
                self.order_repo.add_order_item(
                    order_id=order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=price,
                )
                self.product_repo.adjust_stock(item.product_id, -item.quantity)
                total += price * item.quantity

            self.order_repo.update_order_total(order_id, total)
            self.db.commit()
            order = self.order_repo.get_order_by_id(order_id)
            return order
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise ValidationError("Invalid user_id or product_id reference") from exc
        except ValidationError:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise ValidationError(f"Order failed: {exc}") from exc

    def list_orders(
        self,
        *,
        user_id: Optional[int],
        status: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Dict]:
        return self.order_repo.list_orders(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    def get_order_details(self, order_id: int) -> Dict:
        order = self.order_repo.get_order_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        order["items"] = self.order_repo.list_order_items(order_id)
        return order
