class Product:
    def __init__(self, id, name: str, price: float, stock: int):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def is_in_stock(self) -> bool:
        return self.stock > 0

    def apply_discount(self, percentage: float) -> None:
        if 0 < percentage < 100:
            discount_amount = self.price * (percentage / 100)
            self.price -= discount_amount
            
    def restock(self, amount: int) -> None:
        if amount > 0:
            self.stock += amount
    
    def get_id(self) -> int:
        return self.id
    
    def get_name(self) -> str:
        return self.name
    
    def get_price(self) -> float:
        return self.price
    
    def get_stock(self) -> int:
        return self.stock
    
    def display_product_info(self) -> str:
        return f"Product ID: {self.id}, Name: {self.name}, Price: ${self.price:.2f}, Stock: {self.stock}"
    
    def update_price(self, new_price: float) -> float:
        if new_price >= 0:
            self.price = new_price
        return self.price
    
    def update_name(self, new_name: str) -> str:
        self.name = new_name
        return self.name
    
    def update_stock(self, new_stock: int) -> int:
        if new_stock >= 0:
            self.stock = new_stock
        return self.stock
    
   
    def reduce_stock(self, amount: int) -> None:
        if 0 < amount <= self.stock:
            self.stock -= amount    
            
    def increase_stock(self, amount: int) -> None:
        if amount > 0:
            self.stock += amount
    
    def set_price(self, price: float) -> None:
        if price >= 0:
            self.price = price
            
    @property
    def price_with_tax(self) -> float:
        tax_rate = 0.1  # 10% tax
        return self.price * (1 + tax_rate)
    
    @property
    def is_available(self) -> bool:
        return self.stock > 0
    
    
    def set_name(self, name: str) -> None:
        self.name = name    
        
    @staticmethod
    def error_message() -> str:
        return "An error has occurred in the Product class."
        
    
    def all_errors(self,) -> list:
        errors = []
        if self.price < 0:
            errors.append("Price cannot be negative.")
        if self.stock < 0:
            errors.append("Stock cannot be negative.")
        if not self.name:
            errors.append("Name cannot be empty.")
        if not self.id:
            errors.append("ID cannot be empty.")
        if not self.name.isalnum():
            errors.append("Name must be alphanumeric.")
        if not isinstance(self.price, (int, float)):
            errors.append("Price must be a number.")
        
        return errors