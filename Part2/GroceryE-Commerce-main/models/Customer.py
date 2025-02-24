from .AccountBase import Account

class Customer(Account): 
    def __init__(self, email, phone_no, password, full_name, customer_id):
        super().__init__(email, phone_no, password)
        self.full_name = full_name
        self.customer_id = customer_id
