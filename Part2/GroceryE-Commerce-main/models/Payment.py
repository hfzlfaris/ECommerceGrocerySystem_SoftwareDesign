from Product import Product

class Payment(Subject): 
    def __init__(self, payment_ID, payment_Method, payment_Status, payment_Amount): 
        super().__init__()
        self.order_Quantity = 0 
        self.product_ID = ""
        self.product_Price = 0.0

    def confirm_payment(self, customer): 
        notification = Notification("001",  "Payment confirmed", customer.email)
        self.notify_observers(notification)


