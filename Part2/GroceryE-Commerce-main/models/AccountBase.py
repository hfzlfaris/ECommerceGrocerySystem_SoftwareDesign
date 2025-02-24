from abc import ABC, abstractmethod
import csv

class Account(ABC): 
    def __init__(self, email, phone_no, password):
        self.email = email
        self.phone_no = phone_no
        self.password = password

    def sign_in(self, email, password):
        return self.email == email and self.password == password

    @staticmethod
    def save_account_to_csv(account, account_type):
        filename = f"{account_type}_accounts.csv"
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if account_type == "customer":
                writer.writerow([account.email, account.phone_no, account.password, account.full_name, account.customer_id])
            elif account_type == "retailer":
                writer.writerow([account.email, account.phone_no, account.password, account.retailer_desc])

    @staticmethod
    def load_accounts_from_csv(account_type):
        filename = f"{account_type}_accounts.csv"
        accounts = []
        try:
            with open(filename, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    accounts.append(row)  # Avoid direct dependency
        except FileNotFoundError:
            print(f"No existing {account_type} accounts found. Starting fresh.")
        return accounts
