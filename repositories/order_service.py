from models.order import Order
from repositories.user_repo import UserRepository
from repositories.product_repo import ProductRepository
from repositories.order_repo import OrderRepository


class OrderService:
    def __init__(
        self,
        user_repo: UserRepository,
        product_repo: ProductRepository,
        order_repo: OrderRepository,
    ):
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    def create_simple_order(
        self,
        *,
        order_id: int,
        user_id: int,
        product_id: int,
        quantity: int,
        address: str,
    ) -> int:

        # --- USER ---
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User does not exist.")

        # --- PRODUCT ---
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product does not exist.")

        _, _, _, stock = product
        if stock < quantity:
            raise ValueError("Not enough stock.")

        # --- ORDER DOMAIN ---
        order = Order(order_id, user_id, address)
        order.add_product(product, quantity)
        order.confirm()

        # --- DB TRANSACTION ---
        self.product_repo.autocommit = False
        self.order_repo.autocommit = False
        self.user_repo.autocommit = False

        try:
            new_order_id = self.order_repo.create_order(order)
            self.product_repo.adjust_stock(product_id, -quantity)

            self.order_repo.db.commit()
            return new_order_id
        except Exception:
            self.order_repo.db.rollback()
            raise
        finally:
            self.product_repo.autocommit = True
            self.order_repo.autocommit = True
            self.user_repo.autocommit = True
