from PaymentBuilder import PaymentBuilder
from Product import Product

class PaymentReceipt(PaymentBuilder):
    def __init__self(self, product_Price, tax_rate, shipping_fee):
        self.product_Price = product_Price
        self.tax_rate = tax_rate
        self.shipping_fee = shipping_fee

    def productPrice(self): 
        return self.product_Price

    def addedTax(self): 
        return self.product_Price * self.tax_rate
    
    def shippingCost(self): 
        return self.shipping_fee

    def totalPrice(self): 
        return self.productPrice() + self.addedTax() + self.shippingCost()
    
