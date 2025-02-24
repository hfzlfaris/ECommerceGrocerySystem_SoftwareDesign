import os
import csv  # Added this import back for CSV handling

class Product:
    def __init__(self, product_Name, product_ID, product_Desc, product_Price, stock_Availability, product_Discount, product_Rating, category):
        self.product_Name = product_Name
        self.product_ID = product_ID
        self.product_Desc = product_Desc
        self.product_Price = product_Price
        self.stock_Availability = stock_Availability
        self.product_Discount = product_Discount
        self.product_Rating = product_Rating
        self.category = category

    def calculate_discount(self):
        return self.product_Price * (self.product_Discount / 100)

    def update_stock(self, quantity):
        if self.stock_Availability >= quantity:
            self.stock_Availability -= quantity
            return True
        return False

    @staticmethod
    def load_products_from_csv():
        # Get the directory where the current file (product.py) is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the root directory and then into the data directory
        csv_path = os.path.join(os.path.dirname(current_dir), 'data', 'products.csv')
        products = []
        try:
            with open(csv_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    product = Product(
                        product_Name=row['product_Name'],
                        product_ID=row['product_ID'],
                        product_Desc=row['product_Desc'],
                        product_Price=float(row['product_Price']),
                        stock_Availability=int(row['stock_Availability']),
                        product_Discount=float(row['product_Discount']),
                        product_Rating=float(row['product_Rating']),
                        category=row['category']
                    )
                    products.append(product)
        except FileNotFoundError:
            print("Products.csv not found")
        except Exception as e:
            print(f"Error loading products: {e}")
        return products

    @staticmethod
    def get_product_by_id(product_id):
        products = Product.load_products_from_csv()
        for product in products:
            if product.product_ID == product_id:
                return product
        return None

    @staticmethod
    def get_product_by_name(product_name):
        """Fetch a product by its name from the CSV."""
        products = Product.load_products_from_csv()
        for product in products:
            if product.product_Name == product_name:
                return product
        return None
