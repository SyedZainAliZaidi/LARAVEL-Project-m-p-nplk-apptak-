import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect("mp_studio.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS field_visits;
DROP TABLE IF EXISTS sales_activity;
DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS warehouse_stock;

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE,
    customer_name TEXT,
    product_name TEXT,
    quantity INTEGER,
    total_amount REAL,
    status TEXT,
    order_type TEXT,
    department TEXT,
    created_at TEXT
);

CREATE TABLE shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT,
    tracking_id TEXT UNIQUE,
    courier_center TEXT,
    rider_name TEXT,
    status TEXT,
    department TEXT,
    last_updated TEXT
);

CREATE TABLE field_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rep_name TEXT,
    pharmacy_or_doctor TEXT,
    city TEXT,
    visit_date TEXT,
    check_in_time TEXT,
    department TEXT,
    notes TEXT
);

CREATE TABLE sales_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rep_name TEXT,
    product_name TEXT,
    units_sold INTEGER,
    revenue REAL,
    department TEXT,
    activity_date TEXT
);

CREATE TABLE support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT UNIQUE,
    customer_name TEXT,
    product_name TEXT,
    issue_type TEXT,
    status TEXT,
    department TEXT,
    created_at TEXT
);

CREATE TABLE warehouse_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    quantity_available INTEGER,
    warehouse_location TEXT,
    department TEXT,
    last_updated TEXT
);
""")

products = ["Panadol Extra 500mg", "Augmentin 625mg", "Brufen 400mg", "Disprin", "Calpol Syrup", "Rigix Tablets"]
electronics = ["Samsung Galaxy A54", "Samsung Galaxy Tab", "Samsung Buds", "Samsung Watch 6"]
customers_b2b = ["City Pharmacy Lahore", "Metro Medical Store Karachi", "Al-Shifa Pharmacy Islamabad", "HealthPlus Multan"]
customers_b2c = ["Ahmed Raza", "Fatima Khan", "Bilal Hussain", "Ayesha Malik", "Usman Tariq"]
reps = ["Hassan Ali", "Zainab Sheikh", "Omer Farooq", "Sana Iqbal"]
telecom_reps = ["Waqas Ahmed", "Mahnoor Siddiqui"]
cities = ["Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan"]
courier_centers = ["Lahore Hub", "Karachi Central", "Islamabad North"]
statuses = ["pending", "confirmed", "shipped", "delivered"]
warehouses = ["Lahore Warehouse", "Karachi Warehouse", "Islamabad Warehouse"]

def rand_date(days_back=30):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime("%Y-%m-%d %H:%M")

order_numbers = []
for i in range(1, 31):
    order_number = f"APT-{2026000 + i}"
    order_type = random.choice(["b2b", "b2c"])
    customer = random.choice(customers_b2b if order_type == "b2b" else customers_b2c)
    product = random.choice(products)
    qty = random.randint(1, 200) if order_type == "b2b" else random.randint(1, 5)
    unit_price = round(random.uniform(50, 800), 2)
    status = random.choice(statuses)
    cur.execute("""
        INSERT INTO orders (order_number, customer_name, product_name, quantity, total_amount, status, order_type, department, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_number, customer, product, qty, round(qty * unit_price, 2), status, order_type, "pharma_sales", rand_date()))
    order_numbers.append(order_number)

cur.execute("SELECT order_number, status FROM orders WHERE status IN ('shipped', 'delivered')")
for order_number, status in cur.fetchall():
    tracking_id = f"TRK-{random.randint(100000, 999999)}"
    ship_status = "delivered" if status == "delivered" else random.choice(["in_transit", "out_for_delivery"])
    cur.execute("""
        INSERT INTO shipments (order_number, tracking_id, courier_center, rider_name, status, department, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (order_number, tracking_id, random.choice(courier_centers), random.choice(reps), ship_status, "logistics", rand_date(5)))

for i in range(25):
    cur.execute("""
        INSERT INTO field_visits (rep_name, pharmacy_or_doctor, city, visit_date, check_in_time, department, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        random.choice(reps),
        random.choice(["Dr. Aslam Clinic", "City Pharmacy", "Green Cross Pharmacy", "Dr. Rabia's Clinic"]),
        random.choice(cities),
        rand_date(14),
        f"{random.randint(9,17)}:{random.choice(['00','15','30','45'])}",
        "pharma_field",
        random.choice(["Discussed new product line", "Restocked samples", "Follow-up visit", "Introduced discount scheme"])
    ))

for i in range(25):
    units = random.randint(5, 100)
    revenue = round(units * random.uniform(50, 800), 2)
    cur.execute("""
        INSERT INTO sales_activity (rep_name, product_name, units_sold, revenue, department, activity_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (random.choice(reps), random.choice(products), units, revenue, "pharma_sales", rand_date(14)))

for i in range(15):
    units = random.randint(3, 60)
    revenue = round(units * random.uniform(15000, 90000), 2)
    cur.execute("""
        INSERT INTO sales_activity (rep_name, product_name, units_sold, revenue, department, activity_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (random.choice(telecom_reps), random.choice(electronics), units, revenue, "telecom_sales", rand_date(14)))

issue_types = ["Screen repair", "Battery replacement", "Warranty claim", "Software issue", "Physical damage"]
ticket_statuses = ["received", "in_repair", "ready_for_pickup", "delivered"]
for i in range(20):
    ticket_number = f"SUP-{5000 + i}"
    cur.execute("""
        INSERT INTO support_tickets (ticket_number, customer_name, product_name, issue_type, status, department, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_number,
        random.choice(customers_b2c),
        random.choice(electronics),
        random.choice(issue_types),
        random.choice(ticket_statuses),
        "telecom_support",
        rand_date(20)
    ))

for product in products + electronics:
    for warehouse in warehouses:
        cur.execute("""
            INSERT INTO warehouse_stock (product_name, quantity_available, warehouse_location, department, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (product, random.randint(0, 5000), warehouse, "logistics", rand_date(3)))

conn.commit()
conn.close()

print("seeded", len(order_numbers), "orders across pharma_sales, telecom_sales, telecom_support, logistics, pharma_field")