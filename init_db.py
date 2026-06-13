import sqlite3
from datetime import datetime, timedelta
import random

def initialize_database():
    # Connect to local file database
    conn = sqlite3.connect("saas_dashboard.db")
    cursor = conn.cursor()

    # 1. Create USERS Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # 2. Create SUBSCRIPTIONS Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL, -- 'Free', 'Pro', 'Enterprise'
        status TEXT NOT NULL,    -- 'active', 'cancelled'
        price REAL NOT NULL,
        started_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 3. Create USAGE LOGS Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,     -- 'api_call', 'data_export', 'dashboard_view'
        units_used INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # --- POPULATE WITH MOCK DATA ---
    print("Generating mock data...")
    
    # Generate mock users
    first_names = ["Amit", "Neha", "Rahul", "Priya", "Vikram", "Rohan", "Sneha", "Anjali"]
    last_names = ["Sharma", "Verma", "Gupta", "Mehta", "Joshi", "Patel", "Rao", "Nair"]
    plans = [("Free", 0.0), ("Pro", 29.0), ("Enterprise", 149.0)]
    actions = [("api_call", 5), ("data_export", 1), ("dashboard_view", 1)]

    base_date = datetime(2026, 5, 1)

    for i in range(1, 21):  # Create 20 users
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '.')}@example.com"
        # Stagger signup dates over the month
        signup_date = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        signup_str = signup_date.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)", (name, email, signup_str))
        user_id = cursor.lastrowid

        # Assign a subscription
        plan_name, price = random.choice(plans)
        status = "active" if random.random() > 0.15 else "cancelled"
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan_name, status, price, started_at) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, plan_name, status, price, signup_str))

        # Generate 5-15 random usage logs per user after their signup date
        for _ in range(random.randint(5, 15)):
            action, base_units = random.choice(actions)
            units = base_units * random.randint(1, 10)
            log_date = signup_date + timedelta(days=random.randint(0, 10), hours=random.randint(1, 12))
            log_str = log_date.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO usage_logs (user_id, action, units_used, timestamp) 
                VALUES (?, ?, ?, ?)
            """, (user_id, action, units, log_str))

    conn.commit()
    conn.close()
    print("Database 'saas_dashboard.db' initialized with rich metrics data successfully!")

if __name__ == "__main__":
    initialize_database()