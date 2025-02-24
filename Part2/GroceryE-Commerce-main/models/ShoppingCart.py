from models.CartItem import CartItem
from models.Product import Product
import csv

class ShoppingCart:
    def __init__(self):
        self.items = []  # List to hold CartItem objects

    def add_product(self, product: Product, quantity: int):
        # Check if product already exists in the cart
        for item in self.items:
            if item.product_ID == product.product_ID:
                item.quantity += quantity  # Update quantity if exists
                return
        # If not, create a new CartItem
        self.items.append(CartItem(product, quantity))

    def remove_product(self, product_id: int):
        # Remove product from the cart
        self.items = [item for item in self.items if item.product_ID != product_id]

    def update_product(self, product_id: int, quantity: int):
        # Update the quantity of a specific product
        for item in self.items:
            if item.product_ID == product_id:
                item.quantity = quantity
                return

    def get_product_quantity(self, product_id: int) -> int:
        # Get the quantity of a specific product in the cart
        for item in self.items:
            if item.product_ID == product_id:
                return item.quantity
        return 0

    def get_cart_items(self):
        return self.items  # Return the list of items in the cart

    def restore_from_csv(self, order_id, customer_id, orders_csv):
        """Restore the shopping cart from orders.csv."""
        self.items.clear()  # Clear current cart items
        try:
            with open(orders_csv, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['order_ID'] == order_id and row['customer_ID'] == customer_id:
                        product_names = eval(row['product_Name'])
                        product_prices = eval(row['product_Price'])
                        product_quantities = eval(row['product_Quantity'])

                        for name, price, quantity in zip(product_names, product_prices, product_quantities):
                            product = Product.get_product_by_name(name)  # Assuming Product has this method
                            if product:
                                self.add_product(product, quantity)
        except Exception as e:
            print(f"Error restoring cart from CSV: {e}")
