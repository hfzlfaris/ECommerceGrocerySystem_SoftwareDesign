from abc import ABC, abstractmethod

class AccountFactory(ABC):  # Abstract Factory
    @abstractmethod
    def create_account(self):
        pass


class CustomerAccountFactory(AccountFactory):  # Concrete Factory
    def create_account(self):
        from .Customer import Customer  # Function-level import
        return Customer(email="", phone_no="", password="", full_name="", customer_id=0)


class RetailerAccountFactory(AccountFactory):  # Concrete Factory
    def create_account(self):
        from .Retailer import Retailer  # Function-level import
        return Retailer(email="", phone_no="", password="", company_name="")
