from models.PaymentMethod import PaymentMethod

class CreditCardPayment(PaymentMethod):
    def __init__(self): 
        super().__init__() 
        self.card_Number = ""
        self.expiry_Date = "" 
        self.cvv = ""

    def set_card_details(self, card_number, expiry_date, cvv):
        # Validate card number (must be 16 digits)
        if len(card_number) == 16 and card_number.isdigit():
            self.card_Number = card_number
        else:
            raise ValueError("Card number must be exactly 16 digits.")

        # Validate CVV (must be 3 digits)
        if len(cvv) == 3 and cvv.isdigit():
            self.cvv = cvv
        else:
            raise ValueError("CVV must be exactly 3 digits.")

        # Validate expiry date (format MM/YY)
        if expiry_date and len(expiry_date) == 5 and expiry_date[2] == '/':
            month, year = expiry_date.split('/')
            if len(month) == 2 and len(year) == 2 and month.isdigit() and year.isdigit() and 1 <= int(month) <= 12:
                self.expiry_Date = expiry_date
            else:
                raise ValueError("Invalid expiry date. Use MM/YY format.")
        else:
            raise ValueError("Expiry date must be in MM/YY format and not exceed 5 characters.")


    def payment_Amount(self):
        return self.amount
