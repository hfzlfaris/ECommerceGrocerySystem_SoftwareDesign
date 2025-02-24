from .AccountBase import Account  # Import a shared base class to avoid circular dependency

class Retailer(Account):  # Concrete Product
    def __init__(self, email="", phone_no="", password="", company_name=""):
        super().__init__(email, phone_no, password)
        self.company_name = company_name
