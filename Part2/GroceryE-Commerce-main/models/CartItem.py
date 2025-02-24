from flask import url_for
from models.Product import Product  

class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity  # Store quantity of the product

    @property
    def product_ID(self):
        return self.product.product_ID

    @property
    def product_name(self):
        return self.product.product_Name

    @property
    def product_price(self):
        return self.product.product_Price

    @property
    def product_image_url(self):
        return url_for('static', filename=f'images/product_images/{self.product.product_ID}.png')