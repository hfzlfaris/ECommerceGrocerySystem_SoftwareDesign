from flask import Flask, redirect, url_for, request, render_template, session, g
from models.Customer import Customer
from models.Retailer import Retailer
from models.Product import Product
from models.ShoppingCart import ShoppingCart
from models.CreditCardPayment import CreditCardPayment

import ast
import csv
import os
import random
import string
from datetime import datetime

app = Flask(__name__)
app.secret_key = "grocery e-commerce"
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in a file

users = {"user@example.com": {"password": "password123", "user_id": "1001"}}


ORDERS_CSV = os.path.join('data', 'orders.csv')
RECEIPTS_CSV = os.path.join('data', 'receipts.csv')
DETAILS_CSV = os.path.join('data', 'details.csv')
ORDER_TRACKER_CSV = os.path.join('data', 'order_tracker.csv')

# Initialize ShoppingCart
shopping_cart = ShoppingCart()

if not os.path.exists(ORDERS_CSV):
    with open(ORDERS_CSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['order_ID', 'customer_ID', 'order_Status', 'order_Date', 'product_Name', 'product_Price', 'product_Quantity', 'total_Amount', 'discounted_Price', 'delivery_Date'])

if not os.path.exists(RECEIPTS_CSV):
    with open(RECEIPTS_CSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['receipt_ID', 'order_ID', 'order_Date', 'product_Name', 'product_Price', 'product_Quantity', 'total_Amount', 'discounted_Price', 'delivery_Date'])

if not os.path.exists(DETAILS_CSV):
    with open(DETAILS_CSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['order_ID', 'address_line1', 'address_line2', 'city', 'state', 'postcode', 'country', 'card_number', 'expiry_date', 'cvv'])

def generate_order_id():
    return f"O{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"

# This function is executed at every request to ensure user is logged in; redirects to login if user is not logged in
@app.before_request
def before_request():
    allowed_routes =  ['login', 'register', 'static', 'home', 'checkout', 'order']
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

    order_id = session.get('order_id')
    customer_id = session.get('user', {}).get('email')

    # Default cart quantity is zero
    g.cart_quantity = 0

    if order_id and customer_id:
        try:
            with open(ORDERS_CSV, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['order_ID'] == order_id and row['customer_ID'] == customer_id:
                        # Sum the product quantities in the current order
                        product_quantities = eval(row['product_Quantity'])
                        g.cart_quantity = sum(product_quantities)
                        break
        except FileNotFoundError:
            print("orders.csv not found.")
        except Exception as e:
            print(f"Error reading orders.csv: {e}")


# Define the path to the accounts.csv file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'data', 'accounts.csv')

@app.route('/home/')
def home():
    breadcrumb = [{'url': url_for('home'), 'text': 'Home'}]
    g.notifications = []

    customer_id = session.get('user', {}).get('email')
    if customer_id:
        try:
            with open(ORDERS_CSV, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['customer_ID'] == customer_id and row['order_Status'] == 'In cart':
                        product_quantities = eval(row['product_Quantity'])
                        if sum(product_quantities) > 0:
                            g.notifications.append("You have items in your cart. Don't forget to complete your purchase!")
                            break
        except FileNotFoundError:
            pass

    return render_template('home.html', breadcrumb=breadcrumb)

@app.before_request
def load_cart_count():
    g.cart_count = session.get("cart_count", 0)

# LOGIN ROUTE
@app.route('/login/', methods=['GET', 'POST'])
def login():
    error_message = None  # Variable to store error message at the start

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Open the accounts.csv file and check login credentials
            with open(CSV_FILE_PATH, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    if row[0] == email and row[2] == password:  
                        # Store user details in session
                        session['user'] = {
                            'customer_ID': row[0],  # Email as customer_ID
                            'role': row[3],  # Role (customer/admin)
                            'full_name': row[4]  # Full name
                        }
                        print("Debug: User logged in ->", session['user'])  # Debugging output

                        # Redirect to home page based on role
                        if row[3] == 'customer':
                            customer = Customer(row[0], row[1], row[2], row[4], row[5])
                            return render_template('home.html', customer=customer)
                        elif row[3] == 'admin':
                            retailer = Retailer(row[0], row[1], row[2], row[4])
                            return render_template('home.html', retailer=retailer)

                # If no matching credentials are found
                error_message = "Invalid email or password. Please try again."

        except FileNotFoundError:
            error_message = "Accounts file not found."

        except Exception as e:
            print(f"Error during login: {e}")
            error_message = "An error occurred. Please try again."

    # If login fails, re-render login page with error
    return render_template('login.html', error_message=error_message)

# LOGOUT ROUTE
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('login'))  # Redirect to login page

# REGISTER ROUTE
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        customer_id = request.form.get('customer_id')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        password = request.form.get('password')

        role = "customer"  # Default role is customer

        try:
            # Append the new user to the accounts.csv file
            with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                data = [email, phone_no, password, role, full_name, customer_id]
                writer.writerow(data)

            # Redirect to login page after successful registration
            return redirect(url_for('login'))

        except FileNotFoundError:
            return render_template('register.html', error_message="Accounts file not found. Please contact support.")

        except Exception as e:
            print(f"Error during registration: {e}")
            return render_template('register.html', error_message="Registration failed. Please try again.")

    return render_template('register.html')

@app.route('/shop')
def shop():
    if 'user' not in session:  # check if user is logged in; if not, redirect to login page
        return redirect(url_for('login'))

    products = Product.load_products_from_csv()

    return render_template('shop.html', products=products)

@app.route('/add_to_cart/<product_id>/', methods=['POST'])
def add_to_cart(product_id):
    product = Product.get_product_by_id(product_id)
    if not product:
        print(f"Error: Product with ID {product_id} not found.")
        return redirect(url_for('view_cart'))

    customer_id = session['user'].get('customer_ID')

    # Ensure session order_id is set correctly
    if 'order_id' not in session or not is_order_pending(session['order_id']):
        try:
            with open(ORDERS_CSV, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['customer_ID'] == customer_id and row['order_Status'] == 'In cart':
                        session['order_id'] = row['order_ID']
                        session.modified = True
                        break
        except FileNotFoundError:
            pass

        if 'order_id' not in session:
            session['order_id'] = generate_order_id()
            session.modified = True
            add_new_order(session['order_id'])

    order_id = session['order_id']

    # Read orders from CSV
    try:
        orders = []
        with open(ORDERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            orders = list(reader)
    except FileNotFoundError:
        orders = []  # If file doesn't exist, start fresh
    except Exception as e:
        print(f"Error reading orders.csv: {e}")
        return redirect(url_for('view_cart'))

    # Update or create order
    order_exists = False
    for order in orders:
        if order['order_ID'] == order_id and order['customer_ID'] == customer_id:
            product_names = eval(order['product_Name'])
            product_prices = eval(order['product_Price'])
            product_quantities = eval(order['product_Quantity'])

            if product.product_Name in product_names:
                index = product_names.index(product.product_Name)
                product_quantities[index] += 1
            else:
                product_names.append(product.product_Name)
                product_prices.append(product.product_Price)
                product_quantities.append(1)

            order['product_Name'] = product_names
            order['product_Price'] = product_prices
            order['product_Quantity'] = product_quantities
            order['total_Amount'] = round(sum(product_prices[i] * product_quantities[i] for i in range(len(product_prices))), 2)
            order['discounted_Price'] = round(order['total_Amount'] * 0.9, 2)
            order_exists = True
            break

    if not order_exists:
        new_order = {
            'order_ID': order_id,
            'customer_ID': customer_id,
            'order_Status': 'In cart',
            'order_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product_Name': [product.product_Name],
            'product_Price': [product.product_Price],
            'product_Quantity': [1],
            'total_Amount': round(product.product_Price, 2),
            'discounted_Price': round(product.product_Price * 0.9, 2),
            'delivery_Date': ""
        }
        orders.append(new_order)

    # Save updated orders to the CSV
    try:
        with open(ORDERS_CSV, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=orders[0].keys())
            writer.writeheader()
            writer.writerows(orders)
    except Exception as e:
        print(f"Error updating orders.csv: {e}")

    return redirect(url_for('view_cart'))


def is_order_pending(order_id):
    """Check if the current order is pending or in cart."""
    try:
        with open(ORDERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['order_ID'] == order_id and row['order_Status'] in ['In cart', 'Pending']:
                    return True
    except FileNotFoundError:
        pass
    return False

@app.route('/orders')
def orders_page():
    return render_template('orders.html', orders=orders)

@app.route("/order_confirmation", methods=["POST"])
def order_confirmation():
    # Assuming order_id and other order details are available from the form
    order_id = request.form["order_ID"]
    
    # Add the order to the order tracker
    add_order_to_tracker(order_id)
    
    # Confirm the order and redirect
    return redirect(url_for('orders'))

def get_order_status(order_id, tracker_file="order_tracker.csv"):
    try:
        with open(tracker_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(f"Checking row: {row}")  # Debugging
                if str(row["order_ID"]) == str(order_id):  # Ensure matching format
                    return row["completion_Status"]  # Return completion status if found
        return "Order not found"  # Default return if order_id isn't found
    except FileNotFoundError:
        return "Error: Order Tracker CSV file not found."

@app.route("/track_order/<order_id>")
def track_order(order_id): 
    # Get the order status from the order_tracker.csv file
    order_status = get_order_status(order_id)  # This will fetch the status from the tracker file
    
    if order_status == "Order not found":
        return "Order not found", 404  # If not in tracker file, return an error
    # Pass the order and order status to the template
    return render_template("track_order.html", order_id=order_id, order_status=order_status)

@app.route('/cart/')
def view_cart():
    order_id = session.get('order_id')
    customer_id = session['user'].get('customer_ID')

    if order_id and customer_id:
        shopping_cart.restore_from_csv(order_id, customer_id, ORDERS_CSV)

    cart_items = shopping_cart.get_cart_items()
    cart_subtotal = sum(item.product_price * item.quantity for item in cart_items)
    cart_total = cart_subtotal
    total_items = sum(item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, cart_subtotal=cart_subtotal, cart_total=cart_total, total_items=total_items)

@app.route('/remove_from_cart/<product_id>/', methods=['POST'])
def remove_from_cart(product_id):
    order_id = session.get('order_id')
    customer_id = session['user'].get('customer_ID')

    if not order_id or not customer_id:
        return redirect(url_for('view_cart'))

    try:
        orders = []
        with open(ORDERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            orders = list(reader)

        updated_orders = []
        for order in orders:
            if order['order_ID'] == order_id and order['customer_ID'] == customer_id:
                product_names = ast.literal_eval(order['product_Name'])
                product_prices = ast.literal_eval(order['product_Price'])
                product_quantities = ast.literal_eval(order['product_Quantity'])

                # Remove the product by its ID
                if product_id in product_names:
                    index = product_names.index(product_id)
                    product_names.pop(index)
                    product_prices.pop(index)
                    product_quantities.pop(index)

                # Update the order details
                order['product_Name'] = product_names
                order['product_Price'] = product_prices
                order['product_Quantity'] = product_quantities
                order['total_Amount'] = round(sum(product_prices[i] * product_quantities[i] for i in range(len(product_prices))), 2)
                order['discounted_Price'] = round(order['total_Amount'] * 0.9, 2)

            updated_orders.append(order)

        # Save updated orders to the CSV
        with open(ORDERS_CSV, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=orders[0].keys())
            writer.writeheader()
            writer.writerows(updated_orders)

    except Exception:
        return redirect(url_for('view_cart'))

    return redirect(url_for('view_cart'))

@app.route('/update_cart/', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    action = request.form.get('action')
    product = Product.get_product_by_id(product_id)

    if not product:
        print(f"Product with ID {product_id} not found.")
        return redirect(url_for('view_cart'))

    order_id = session.get('order_id')
    if not order_id:
        print("No order ID found for this session.")
        return redirect(url_for('view_cart'))

    customer_id = session['user'].get('customer_ID')

    try:
        orders = []
        with open(ORDERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            orders = list(reader)

        for order in orders:
            if order['order_ID'] == order_id and order['customer_ID'] == customer_id:
                product_names = eval(order['product_Name'])
                product_prices = eval(order['product_Price'])
                product_quantities = eval(order['product_Quantity'])

                if product.product_Name in product_names:
                    index = product_names.index(product.product_Name)

                    if action == 'increase':
                        product_quantities[index] += 1
                    elif action == 'decrease' and product_quantities[index] > 1:
                        product_quantities[index] -= 1
                    elif action == 'decrease':
                        product_names.pop(index)
                        product_prices.pop(index)
                        product_quantities.pop(index)

                order['product_Name'] = product_names
                order['product_Price'] = product_prices
                order['product_Quantity'] = product_quantities
                order['total_Amount'] = round(sum(product_prices[i] * product_quantities[i] for i in range(len(product_prices))), 2)
                order['discounted_Price'] = round(order['total_Amount'] * 0.9, 2)
                break

        with open(ORDERS_CSV, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=orders[0].keys())
            writer.writeheader()
            writer.writerows(orders)

    except Exception as e:
        print(f"Error updating orders.csv: {e}")
    return redirect(url_for('view_cart'))

@app.route('/checkout/')
def checkout():
    if 'order_id' not in session:
        print("No order ID found for this session.")
        return redirect(url_for('view_cart'))

    order_id = session['order_id']
    customer_id = session['user'].get('customer_ID')

    # Update the order status to "Pending"
    try:
        orders = []
        with open(ORDERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            orders = list(reader)

        for order in orders:
            if order['order_ID'] == order_id and order['customer_ID'] == customer_id:
                order['order_Status'] = 'Pending'

        with open(ORDERS_CSV, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=orders[0].keys())
            writer.writeheader()
            writer.writerows(orders)

    except Exception as e:
        print(f"Error updating orders.csv for checkout: {e}")

    cart_items = shopping_cart.get_cart_items()
    cart_subtotal = round(sum(item.product_price * item.quantity for item in cart_items), 2)
    shipping_cost = 5.0  # Example shipping cost
    cart_total = round(cart_subtotal + shipping_cost, 2)
    return render_template('checkout.html', cart_items=cart_items, cart_subtotal=cart_subtotal, shipping_cost=shipping_cost, cart_total=cart_total)


@app.route('/process_payment/', methods=['POST'])
def process_payment():
    # Collect payment and address details from the form
    card_number = request.form.get('card_number')
    expiry_date = request.form.get('expiry_date')
    cvv = request.form.get('cvv')
    address_line1 = request.form.get('address_line1')
    address_line2 = request.form.get('address_line2')
    city = request.form.get('city')
    state = request.form.get('state')
    postcode = request.form.get('postcode')
    country = request.form.get('country')

    order_id = session.get('order_id')
    customer_id = session['user'].get('customer_ID')

    # Ensure an order ID and customer ID exist
    if not order_id or not customer_id:
        return redirect(url_for('view_cart'))

    try:
        # Validate payment details
        credit_card_payment = CreditCardPayment()
        credit_card_payment.set_card_details(card_number, expiry_date, cvv)

        # Retrieve the current order from orders.csv
        orders = []
        with open(ORDERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            orders = list(reader)

        current_order = None
        for order in orders:
            if order['order_ID'] == order_id and order['customer_ID'] == customer_id:
                current_order = order
                break

        if not current_order:
            print("Order not found.")
            return redirect(url_for('view_cart'))

        # Generate a receipt ID with the format Rxxxxx
        receipt_id = f"R{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"

        # Move order to receipts.csv
        cart_items = shopping_cart.get_cart_items()
        total_amount = round(sum(item.product_price * item.quantity for item in cart_items), 2)
        discounted_price = round(total_amount * 0.9, 2)

        with open(RECEIPTS_CSV, 'a', newline='') as receipt_file:
            writer = csv.writer(receipt_file)
            writer.writerow([
                receipt_id, order_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                current_order['product_Name'], current_order['product_Price'],
                current_order['product_Quantity'], total_amount, discounted_price, ""
            ])

        # Save address and payment details to details.csv
        with open(DETAILS_CSV, 'a', newline='') as details_file:
            writer = csv.writer(details_file)
            writer.writerow([
                order_id, address_line1, address_line2, 
                city, state, postcode, country, 
                card_number[-4:], expiry_date, cvv  # Save only last 4 digits of the card number
            ])

        # Mark the order as "Confirmed" in orders.csv
        for order in orders:
            if order['order_ID'] == order_id and order['customer_ID'] == customer_id:
                order['order_Status'] = 'Confirmed'
                break

        # Save updated orders to orders.csv
        with open(ORDERS_CSV, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=orders[0].keys())
            writer.writeheader()
            writer.writerows(orders)

        # Clear the shopping cart and reset session order_id
        shopping_cart.items.clear()
        session.pop('order_id', None)

        return redirect(url_for('payment_confirmation'))

    except Exception as e:
        print(f"Payment processing failed: {e}")
        return render_template('checkout.html', error_message="Payment failed. Please try again."), 400

@app.route('/payment_confirmation/')
def payment_confirmation():
    return render_template('payment_confirmation.html')

@app.route('/receipt/<receipt_id>')
def view_receipt(receipt_id):
    receipt_data = {}
    details_data = {}

    try:
        # Read from receipts.csv
        with open(RECEIPTS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['receipt_ID'] == receipt_id:
                    receipt_data = {
                        'receipt_ID': row['receipt_ID'],
                        'order_ID': row['order_ID'],
                        'order_Date': row['order_Date'],
                        'product_Name': eval(row['product_Name']),
                        'product_Price': eval(row['product_Price']),
                        'product_Quantity': eval(row['product_Quantity']),
                        'total_Amount': float(row['total_Amount']),
                        'discounted_Price': float(row['discounted_Price'])
                    }
                    break
        
        # Read from details.csv
        if receipt_data:
            with open(DETAILS_CSV, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['order_ID'] == receipt_data['order_ID']:
                        details_data = {
                            'address_line1': row['address_line1'],
                            'address_line2': row.get('address_line2', ''),
                            'city': row['city'],
                            'state': row['state'],
                            'postcode': row['postcode'],
                            'country': row['country'],
                            'card_number': row['card_number']
                        }
                        break
    except Exception as e:
        print(f"Error loading receipt: {e}")

    return render_template('receipt.html', receipt_data=receipt_data, details_data=details_data)

def load_orders():
    """Load orders from CSV and return as a list of dictionaries"""
    orders = []
    try:
        with open("orders.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            orders = [row for row in reader]
    except FileNotFoundError:
        print("Orders file not found!")
    return orders

def load_order_status():
    statuses = {}
    try:
        with open(ORDER_TRACKER_CSV, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                statuses[row['order_ID']] = row['completion_Status']
        print(f"Order statuses: {statuses}")  # Debug print
    except FileNotFoundError:
        print("Error: Order tracker CSV file not found.")
    return statuses

def initialize_order_tracker():
    if not os.path.exists(ORDER_TRACKER_CSV):
        with open(ORDER_TRACKER_CSV, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["order_ID", "completion_Status"])
            writer.writeheader()  # Write the header only if file is new

def add_new_order(order_id):
    statuses = load_order_status()  # Load current statuses
    
    # Add the new order with "Pending" status
    statuses[order_id] = "Pending"
    
    # Save the updated statuses back to the CSV
    with open(ORDER_TRACKER_CSV, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["order_ID", "completion_Status"])
        writer.writeheader()
        for order_id, status in statuses.items():
            writer.writerow({"order_ID": order_id, "completion_Status": status})

def update_order_status(order_id, status):
    orders = []
    try:
        with open(ORDER_TRACKER_CSV, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['order_ID'] == order_id:
                    row['completion_Status'] = status  # Update the status
                orders.append(row)

        # Re-write the CSV with updated status
        with open(ORDER_TRACKER_CSV, 'w', newline='', encoding="utf-8") as file:
            fieldnames = ['order_ID', 'completion_Status']  # Make sure your fieldnames match the CSV structure
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(orders)
    except FileNotFoundError:
        print("Error: Order Tracker CSV file not found.")

@app.route('/orders/')
def orders():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirects if user is not logged in

    customer_id = session['user'].get('customer_ID')  # Get email as customer_ID
    print("Debug: Logged-in user ID (email) ->", customer_id)  # Debugging output

    orders = get_orders(customer_id, "data/orders.csv")  # Fetch orders using email as customer_ID
    print("Debug: Orders retrieved ->", orders)  # Debugging output
    
    return render_template('orders.html', orders=orders)  # Pass data to template

import ast

def get_orders(user_id, csv_file="orders.csv"):
    orders = []
    try:
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Read as dictionary
            for row in reader:
                print(row)
                if row["customer_ID"] == str(user_id):  # Match user ID
                    # Parse product_Price as a list and handle accordingly
                    try:
                        product_price_list = ast.literal_eval(row["product_Price"])
                        if isinstance(product_price_list, list):
                            average_price = sum(product_price_list) / len(product_price_list) if product_price_list else 0
                        else:
                            average_price = float(product_price_list)
                    except:
                        average_price = 0
                    
                    # Parse product_Quantity as a list and take the first element (or adjust logic)
                    try:
                        product_quantity_list = ast.literal_eval(row["product_Quantity"])
                        if isinstance(product_quantity_list, list):
                            product_quantity = int(product_quantity_list[0]) if product_quantity_list else 0
                        else:
                            product_quantity = int(product_quantity_list)
                    except:
                        product_quantity = 0
                    
                    orders.append({
                        "order_ID": row["order_ID"],
                        "customer_ID": row["customer_ID"],
                        "completion_Status": row["order_Status"],  # Change here to completion_Status
                        "order_Date": row["order_Date"],
                        "product_Name": row["product_Name"],
                        "product_Price": average_price,  # Use computed price
                        "product_Quantity": product_quantity,  # Use adjusted quantity
                        "total_Amount": float(row["total_Amount"]),  # Ensure total amount is a float
                        "delivery_Date": row["delivery_Date"]
                    })
    except FileNotFoundError:
        print("Error: Orders CSV file not found.")
    
    return orders

#About us
@app.route('/about_us')
def about_us():

    return render_template('about_us.html')

@app.route('/')
def default_route():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)