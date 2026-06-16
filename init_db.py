import sqlite3
from datetime import datetime, timedelta
import random

def initialize_database():
    conn = sqlite3.connect("saas_dashboard.db")
    cursor = conn.cursor()

    # Drop existing tables to avoid duplicate append errors during regeneration
    cursor.execute("DROP TABLE IF EXISTS usage_logs")
    cursor.execute("DROP TABLE IF EXISTS subscriptions")
    cursor.execute("DROP TABLE IF EXISTS users")

    # 1. Create Tables
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL, 
        status TEXT NOT NULL,    
        price REAL NOT NULL,
        started_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,     
        units_used INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    print("Generating expanded enterprise-grade mock data...")
    
    first_names = ["Amit", "Neha", "Rahul", "Priya", "Vikram", "Rohan", "Sneha", "Anjali", "Arjun", "Karan", "Meera", "Kabir", "Tanvi", "Aditya", "Riya", "Yash"]
    last_names = ["Sharma", "Verma", "Gupta", "Mehta", "Joshi", "Patel", "Rao", "Nair", "Das", "Choudhury", "Mishra", "Reddy", "Kulkarni", "Kapoor", "Sen"]
    
    total_users_to_generate = 100
    start_timeline = datetime(2025, 1, 1)

    for i in range(1, total_users_to_generate + 1):
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        name = f"{f_name} {l_name}"
        
        # FIX: We build the email prefix using lowercase parts AND the unique loop counter 'i'
        # This guarantees user 12 and user 45 have completely distinct emails even if both are named 'Amit Sharma'
        email_prefix = f"{f_name.lower()}.{l_name.lower()}.user{i}"
        email = f"{email_prefix}@example.com"
        
        # Distribute signups smoothly over an 18-month timeline
        days_offset = random.randint(0, 520)
        signup_date = start_timeline + timedelta(days=days_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        signup_str = signup_date.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)", (name, email, signup_str))
        user_id = cursor.lastrowid

        # Business logic for Tier assignments
        dice_roll = random.random()
        if dice_roll < 0.15:
            plan_name, price = "Enterprise", 149.0
        elif dice_roll < 0.60:
            plan_name, price = "Pro", 29.0
        else:
            plan_name, price = "Free", 0.0

        status = "active"
        if days_offset < 300 and random.random() < 0.35:
            status = "cancelled"

        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan_name, status, price, started_at) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, plan_name, status, price, signup_str))

        # Generate contextual usage logs
        num_logs = random.randint(30, 80) if plan_name == "Enterprise" else random.randint(10, 35) if plan_name == "Pro" else random.randint(2, 10)
        actions_pool = [("api_call", 5), ("dashboard_view", 1), ("data_export", 10)]

        for _ in range(num_logs):
            action, base_units = random.choice(actions_pool)
            multiplier = random.randint(5, 25) if plan_name == "Enterprise" else random.randint(1, 5)
            units = base_units * multiplier
            
            log_days_offset = random.randint(0, max(1, (datetime(2026, 6, 1) - signup_date).days))
            log_date = signup_date + timedelta(days=log_days_offset, hours=random.randint(0, 12))
            log_str = log_date.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO usage_logs (user_id, action, units_used, timestamp) 
                VALUES (?, ?, ?, ?)
            """, (user_id, action, units, log_str))

    conn.commit()
    conn.close()
    print(f"Successfully loaded {total_users_to_generate} analytical profiles into 'saas_dashboard.db'!")

if __name__ == "__main__":
    initialize_database()