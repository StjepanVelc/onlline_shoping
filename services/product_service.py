import sqlite3
from typing import Dict, List, Optional

from repositories.product_repo import ProductRepository
from services.exceptions import NotFoundError, ValidationError


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, payload) -> Dict:
        try:
            product_id = self.repo.create_product(
                payload.name,
                payload.description,
                payload.price,
                payload.stock,
            )
        except sqlite3.IntegrityError:
            raise ValidationError("Product with this name already exists")

        return self.get_product(product_id)

    def list_products(self, q: Optional[str], limit: int, offset: int) -> List[Dict]:
        return self.repo.list_products(q=q, limit=limit, offset=offset)

    def get_product(self, product_id: int) -> Dict:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def update_product(self, product_id: int, payload) -> Dict:
        fields = {
            key: value
            for key, value in payload.model_dump().items()
            if value is not None
        }
        if not fields:
            raise ValidationError("No fields to update")
        updated = self.repo.update_product(product_id, fields)
        if not updated:
            raise NotFoundError("Product not found")
        return self.get_product(product_id)

    def delete_product(self, product_id: int) -> Dict:
        deleted = self.repo.delete_product(product_id)
        if not deleted:
            raise NotFoundError("Product not found")
        return {"deleted": True, "id": product_id}
