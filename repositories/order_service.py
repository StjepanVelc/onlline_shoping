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
        user_id: int,
        product_id: int,
        quantity: int,
        address: str,
    ) -> int:
        """Create a single-product order and return the new order id."""

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

        # --- DB TRANSACTION ---
        self.product_repo.autocommit = False
        self.order_repo.autocommit = False
        self.user_repo.autocommit = False

        try:
            new_order_id = self.order_repo.create_order(
                user_id=user_id,
                address=address,
                status="confirmed",
            )
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
