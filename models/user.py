import email


class User:
    def __init__(self, id, country, username, email):
        self.id = id
        self.country = country
        self.username = username
        self.email = email

    def get_id(self):
        return self.id

    def get_country(self):
        return self.country

    def get_username(self):
        return self.username

    def get_email(self):
        return self.email
    
    def set_country(self, country):
        self.country = country
        
    def set_username(self, username):
        self.username = username
    
    def update_email(self, new_email):
        self.email = new_email
        return self.email
    
    def display_user_info(self):
        return f"User ID: {self.id}, Username: {self.username}, Email: {self.email}, Country: {self.country}"
    
    
    def update_username(self, new_username):
        self.username = new_username
        return self.username
    
    def all_errors(self):
        errors = []
        if not self.username or len(self.username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if "@" not in self.email or "." not in self.email:
            errors.append("Invalid email format.")
        if not self.country:
            errors.append("Country cannot be empty.")
        if not isinstance(self.id, int) or self.id <= 0:
            errors.append("ID must be a positive integer.")
        if not email.utils.parseaddr(self.email)[1]:
            errors.append("Invalid email address.")
        return errors
    
