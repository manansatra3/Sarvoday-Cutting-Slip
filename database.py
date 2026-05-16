import sqlite3

# Create/connect database
conn = sqlite3.connect("cutting_slip.db")
cur = conn.cursor()

# -----------------------------
# SLIPS TABLE
# -----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS slips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slip_no TEXT,
    date TEXT,
    party TEXT,
    address TEXT,
    cloth TEXT,
    school TEXT,
    item TEXT,
    sizes TEXT,
    qtys TEXT,
    meters TEXT,
    total_qty TEXT,
    total_meter TEXT,
    remark TEXT,
    CREATE TABLE IF NOT EXISTS slips
    status TEXT DEFAULT 'ACTIVE'
)
""")

# -----------------------------
# PARTIES TABLE
# -----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_name TEXT,
    party_address TEXT
)
""")

# -----------------------------
# CLOTH MASTER TABLE
# -----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS cloth_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cloth_name TEXT
)
""")

# -----------------------------
# SCHOOL MASTER TABLE
# -----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT
)
""")

# -----------------------------
# USERS TABLE
# -----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# -----------------------------
# ITEM MASTER TABLE
# -----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    sizes TEXT
)
""")

conn.commit()
conn.close()

print("Database & Tables Created Successfully")