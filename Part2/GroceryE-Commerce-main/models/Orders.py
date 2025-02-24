import csv

def get_orders(user_id, csv_file="orders.csv"):
    orders = []
    try:
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Read as dictionary
            for row in reader:
                print(row)
                if row["customer_ID"] == str(user_id):  # Match user ID
                    orders.append({
                        "order_ID": row["order_ID"],
                        "customer_ID": row["customer_ID"],
                        "completion_Status": row["order_Status"],  # Change here to completion_Status
                        "order_Date": row["order_Date"],
                        "product_Name": row["product_Name"],
                        "product_Price": float(row["product_Price"]),  # Ensure price is a float
                        "product_Quantity": int(row["product_Quantity"]),  # Ensure quantity is an int
                        "total_Amount": float(row["total_Amount"]),  # Ensure total amount is a float
                        "delivery_Date": row["delivery_Date"]
                    })
    except FileNotFoundError:
        print("Error: Orders CSV file not found.")
    
    return orders
