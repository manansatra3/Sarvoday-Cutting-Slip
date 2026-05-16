import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

conn = sqlite3.connect("cutting_slip.db")
cur = conn.cursor()

# =========================
# IMPORT PARTIES
# =========================

party_file = os.path.join(BASE_DIR, "party_master.json")

if os.path.exists(party_file):

    with open(party_file, "r") as f:

        parties = json.load(f)

        for row in parties:

            party = row.get("party", "")
            address = row.get("address", "")

            cur.execute("""
                INSERT INTO parties (
                    party_name,
                    party_address
                )
                VALUES (?, ?)
            """, (party, address))

# =========================
# IMPORT CLOTH
# =========================

cloth_file = os.path.join(BASE_DIR, "cloth_master.json")

if os.path.exists(cloth_file):

    with open(cloth_file, "r") as f:

        cloths = json.load(f)

        for cloth in cloths:

            cur.execute("""
                INSERT INTO cloth_master (
                    cloth_name
                )
                VALUES (?)
            """, (cloth,))

# =========================
# IMPORT SCHOOLS
# =========================

school_file = os.path.join(BASE_DIR, "school_master.json")

if os.path.exists(school_file):

    with open(school_file, "r") as f:

        schools = json.load(f)

        for school in schools:

            cur.execute("""
                INSERT INTO schools (
                    school_name
                )
                VALUES (?)
            """, (school,))

# =========================
# IMPORT ITEMS
# =========================

item_file = os.path.join(BASE_DIR, "item_master.json")

if os.path.exists(item_file):

    with open(item_file, "r") as f:

        items = json.load(f)

        for row in items:

            item = row.get("item", "")
            sizes = ",".join(row.get("sizes", []))

            cur.execute("""
                INSERT INTO items (
                    item_name,
                    sizes
                )
                VALUES (?, ?)
            """, (item, sizes))

conn.commit()
conn.close()

print("JSON Data Imported Successfully")