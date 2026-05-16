from flask import Flask, render_template, request, redirect
import json
import datetime
import os
import pandas as pd
import webbrowser
import threading
import time
from flask import jsonify
from flask import send_file
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "slip_history.json")


def load_history():



    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM slips
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    history = []

    for row in rows:

        history.append({

            "slip_no": row["slip_no"],
            "date": row["date"],
            "party": row["party"],
            "address": row["address"],
            "cloth": row["cloth"],
            "school": row["school"],
            "item": row["item"],

            "remark": row["remark"],

            "sizes": json.loads(row["sizes"]),
            "qtys": json.loads(row["qtys"]),
            "meters": json.loads(row["meters"]),

            "total_qty": row["total_qty"],
            "total_meter": row["total_meter"],
            "status": row["status"]

        })

    return history


    
    items = []

    for row in rows:

        if row[0]:
            items.append(row[0])

    return sorted(list(set(items)))

def save_history(data):

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM slips WHERE slip_no=?",
        (data["slip_no"],)
    )

    existing = cur.fetchone()

    if existing:

        cur.execute("""

            UPDATE slips SET

                date=?,
                party=?,
                address=?,
                cloth=?,
                school=?,
                item=?,
                sizes=?,
                qtys=?,
                meters=?,
                total_qty=?,
                total_meter=?,
                remark=?

            WHERE slip_no=?

        """, (

            data["date"],
            data["party"],
            data["address"],
            data["cloth"],
            data["school"],
            data["item"],
            json.dumps(data["sizes"]),
            json.dumps(data["qtys"]),
            json.dumps(data["meters"]),
            data["total_qty"],
            data["total_meter"],
            data["remark"],
            data["slip_no"]

        ))

    else:

        existing = cur.execute(
            "SELECT id FROM slips WHERE slip_no=?",
            (data["slip_no"],)
        ).fetchone()

        if existing:

            cur.execute("""
                UPDATE slips SET
                    date=?,
                    party=?,
                    address=?,
                    cloth=?,
                    school=?,
                    item=?,
                    sizes=?,
                    qtys=?,
                    meters=?,
                    total_qty=?,
                    total_meter=?,
                    remark=?
                WHERE slip_no=?
            """, (
                data["date"],
                data["party"],
                data["address"],
                data["cloth"],
                data["school"],
                data["item"],
                json.dumps(data["sizes"]),
                json.dumps(data["qtys"]),
                json.dumps(data["meters"]),
                data["total_qty"],
                data["total_meter"],
                data["remark"],
                data["slip_no"]
            ))

        else:

            cur.execute("""
                INSERT INTO slips (
                    slip_no,
                    date,
                    party,
                    address,
                    cloth,
                    school,
                    item,
                    sizes,
                    qtys,
                    meters,
                    total_qty,
                    total_meter,
                    remark,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["slip_no"],
                data["date"],
                data["party"],
                data["address"],
                data["cloth"],
                data["school"],
                data["item"],
                json.dumps(data["sizes"]),
                json.dumps(data["qtys"]),
                json.dumps(data["meters"]),
                data["total_qty"],
                data["total_meter"],
                data["remark"],
                "Active"
            ))

    conn.commit()

    conn.close()

def get_next_slip_no():
    history = load_history()
    return len(history) + 1

from openpyxl import load_workbook

import pandas as pd

def load_party_details():

    file_path = os.path.join(BASE_DIR, "party_master.json")

    party_data = {}

    school_list = []

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        SELECT school_name
        FROM schools
        ORDER BY school_name
    """)

    rows = cur.fetchall()

    for row in rows:

        if row[0]:
            school_list.append(row[0])

    conn.close()

    cloth_list = []

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        SELECT cloth_name
        FROM cloth_master
        ORDER BY cloth_name
    """)

    rows = cur.fetchall()

    for row in rows:

        if row[0]:
            cloth_list.append(row[0])

    conn.close()

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        SELECT party_name, party_address
        FROM parties
    """)

    rows = cur.fetchall()

    for row in rows:

        party = str(row[0]).strip()
        address = str(row[1]).strip()

        if party:
            party_data[party] = address

    conn.close()

    return {
        "party_data": party_data,
        "school_list": school_list,
        "cloth_list": cloth_list
    }

def load_size_map():

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        SELECT item_name, sizes
        FROM items
    """)

    rows = cur.fetchall()

    conn.close()

    size_map = {}

    for row in rows:

        item = str(row[0]).strip()

        sizes = str(row[1]).split(",")

        sizes = [s.strip() for s in sizes if s.strip()]

        if item:
            size_map[item] = sizes

    return size_map

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        slip_no = request.form.get("slip_no")
        
        # Ensure slip_no is stored properly
        try:
            slip_no = int(slip_no) if slip_no else get_next_slip_no()
        except:
            slip_no = get_next_slip_no()
        
        data = {
            "slip_no": str(slip_no),
            "date": datetime.datetime.strptime(
                h["date"],
                "%Y-%m-%d"
            ).strftime("%d-%m-%Y")
            if (h := request.form) and h.get("date") else "",
            "party": request.form.get("party"),
            "address": request.form.get("address"),
            "cloth": request.form.get("cloth"),
            "school": request.form.get("school"),
            "item": request.form.get("item"),
            "sizes": request.form.getlist("size[]"),
            "qtys": request.form.getlist("qty[]"),
            "meters": request.form.getlist("meter[]"),
            "total_qty": request.form.get("total_qty"),
            "total_meter": request.form.get("total_meter"),
            "remark": request.form.get("remark"),
        }

        save_history(data)

        return redirect("/")

    history = load_history()
    
    # Reverse for display
    history_display = list(reversed(history))

    party_list = load_party_data()

    item_list = load_item_data()

    master_data = load_party_details()

    size_map = load_size_map()

    slip_no = get_next_slip_no()

    return render_template(
        "index.html",
        history=history_display,
        party_list=party_list,
        item_list=item_list,
        slip_no=slip_no,
        party_data=master_data["party_data"],
        school_list=master_data["school_list"],
        cloth_list=master_data["cloth_list"],
        size_map=size_map,
        items=item_list
    )

@app.route("/save_party", methods=["POST"])
def save_party():

    data = request.json

    party_name = data.get("party")
    address = data.get("address")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO parties (
            party_name,
            party_address
        )
        VALUES (?, ?)
    """, (party_name, address))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success"
    })


def load_party_data():

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        SELECT party_name
        FROM parties
        ORDER BY party_name
    """)

    rows = cur.fetchall()

    conn.close()

    party_list = []

    for row in rows:

        if row[0]:
            party_list.append(row[0])

    return sorted(list(set(party_list)))   

def load_item_data():

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        SELECT item_name
        FROM items
        ORDER BY item_name
    """)

    rows = cur.fetchall()

    conn.close()

    item_list = []

    for row in rows:

        if row[0]:
            item_list.append(row[0])

    return sorted(list(set(item_list)))

@app.route("/manage_parties")
def manage_parties():

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM parties
        ORDER BY party_name
    """)

    parties = cur.fetchall()

    conn.close()

    return render_template(
        "manage_parties.html",
        parties=parties
    )

        
@app.route("/save_cloth", methods=["POST"])
def save_cloth():

    data = request.get_json()

    cloth = data.get("cloth")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cloth_master (
            cloth_name
        )
        VALUES (?)
    """, (cloth,))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/update_cloth", methods=["POST"])
def update_cloth():

    data = request.json

    old_name = data.get("old_name")
    new_name = data.get("new_name")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cursor = conn.cursor()

    # UPDATE MASTER

    cursor.execute(
        """
        UPDATE cloth_master
        SET cloth_name=?
        WHERE cloth_name=?
        """,
        (new_name, old_name)
    )

    # UPDATE HISTORY

    cursor.execute(
        """
        UPDATE slips
        SET cloth=?
        WHERE TRIM(UPPER(cloth))
            =
              TRIM(UPPER(?))
        """,
        (new_name, old_name)
    )

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/delete_cloth", methods=["POST"])
def delete_cloth():

    data = request.json

    cloth = data.get("cloth_name")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cursor = conn.cursor()

    # CHECK USED

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM slips
        WHERE TRIM(UPPER(cloth))
            =
              TRIM(UPPER(?))
        """,
        (cloth,)
    )

    used = cursor.fetchone()[0]

    if used > 0:

        conn.close()

        return jsonify({
            "status":"error",
            "message":"Cloth already used in slips"
        })

    # DELETE

    cursor.execute(
        """
        DELETE FROM cloth_master
        WHERE TRIM(UPPER(cloth_name))
            =
              TRIM(UPPER(?))
        """,
        (cloth,)
    )

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/save_school", methods=["POST"])
def save_school():

    data = request.get_json()

    school = data.get("school")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO schools (
            school_name
        )
        VALUES (?)
    """, (school,))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/update_school", methods=["POST"])
def update_school():

    data = request.json

    old_name = data.get("old_name")
    new_name = data.get("new_name")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cursor = conn.cursor()

    # UPDATE MASTER

    cursor.execute(
        """
        UPDATE schools
        SET school_name=?
        WHERE school_name=?
        """,
        (new_name, old_name)
    )

    # UPDATE HISTORY

    cursor.execute(
        """
        UPDATE slips
        SET school=?
        WHERE TRIM(UPPER(school))
            =
              TRIM(UPPER(?))
        """,
        (new_name, old_name)
    )

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/delete_school", methods=["POST"])
def delete_school():

    data = request.json

    school = data.get("school_name")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cursor = conn.cursor()

    # CHECK USED

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM slips
        WHERE TRIM(UPPER(school))
            =
              TRIM(UPPER(?))
        """,
        (school,)
    )

    used = cursor.fetchone()[0]

    if used > 0:

        conn.close()

        return jsonify({
            "status":"error",
            "message":"School already used in slips"
        })

    # DELETE

    cursor.execute(
        """
        DELETE FROM schools
        WHERE TRIM(UPPER(school_name))
            =
              TRIM(UPPER(?))
        """,
        (school,)
    )

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/save_item", methods=["POST"])
def save_item():

    data = request.get_json()

    item = data.get("item", "").strip()

    sizes = data.get("sizes", "").strip()

    if not item:

        return jsonify({
            "status":"error",
            "message":"Item required"
        })

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    # CHECK DUPLICATE

    cur.execute("""
        SELECT COUNT(*)
        FROM items
        WHERE TRIM(UPPER(item_name))
            =
              TRIM(UPPER(?))
    """, (item,))

    exists = cur.fetchone()[0]

    if exists > 0:

        conn.close()

        return jsonify({
            "status":"error",
            "message":"Item already exists"
        })

    # SAVE

    cur.execute("""
        INSERT INTO items (
            item_name,
            sizes
        )
        VALUES (?, ?)
    """, (item, sizes))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"success"
    })

@app.route("/update_item", methods=["POST"])
def update_item():

    data = request.json

    old_item = data.get("old_item")
    new_item = data.get("new_item")
    sizes = data.get("sizes")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    cur.execute("""
        UPDATE items
        SET item_name = ?, sizes = ?
        WHERE item_name = ?
    """, (
        new_item,
        sizes,
        old_item
    ))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"success",
        "message":"Item Updated"
    })
    
@app.route("/delete_item", methods=["POST"])
def delete_item():

    data = request.get_json()

    item_name = data.get("item_name")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    cur = conn.cursor()

    # CHECK USED IN SLIPS
    # CHECK USED IN SLIPS

    cur.execute("""
        SELECT COUNT(*)
        FROM slips
        WHERE TRIM(UPPER(item))
            =
            TRIM(UPPER(?))
    """, (item_name,))

    used_count = cur.fetchone()[0]

    if used_count > 0:

        conn.close()

        return jsonify({
            "status": "error",
            "message": "Item is used in slips"
        })

    # DELETE ITEM
    # DELETE ITEM

    cur.execute("""
        DELETE FROM items
        WHERE TRIM(UPPER(item_name))
            =
            TRIM(UPPER(?))
    """, (item_name,))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Item Deleted Successfully"
    })

    
@app.route("/edit_party/<int:id>", methods=["GET", "POST"])
def edit_party(id):

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    if request.method == "POST":

        party_name = request.form.get("party_name")
        party_address = request.form.get("party_address")

        cur.execute("""
            UPDATE parties
            SET
                party_name = ?,
                party_address = ?
            WHERE id = ?
        """, (party_name, party_address, id))

        conn.commit()
        conn.close()

        return redirect("/manage_parties")

    cur.execute("""
        SELECT *
        FROM parties
        WHERE id = ?
    """, (id,))

    party = cur.fetchone()

    conn.close()

    return render_template(
        "edit_party.html",
        party=party
    )


@app.route("/manage_items")
def manage_items():

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM items
        ORDER BY item_name
    """)

    items = cur.fetchall()

    conn.close()

    return render_template(
        "manage_items.html",
        items=items
    )

@app.route("/edit_item/<int:id>", methods=["GET", "POST"])
def edit_item(id):

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    if request.method == "POST":

        item_name = request.form.get("item_name")
        sizes = request.form.get("sizes")

        cur.execute("""
            UPDATE items
            SET
                item_name = ?,
                sizes = ?
            WHERE id = ?
        """, (item_name, sizes, id))

        conn.commit()
        conn.close()

        return redirect("/manage_items")

    cur.execute("""
        SELECT *
        FROM items
        WHERE id = ?
    """, (id,))

    item = cur.fetchone()

    conn.close()

    return render_template(
        "edit_item.html",
        item=item
    )

@app.route("/cancel_slip/<slip_no>")
def cancel_slip(slip_no):

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cur = conn.cursor()

    cur.execute("""
        UPDATE slips
        SET status = 'Cancelled'
        WHERE slip_no = ?
    """, (slip_no,))

    conn.commit()

    conn.close()

    return redirect("/")

@app.route("/export_excel")
def export_excel():

    history = load_history()

    rows = []

    for h in history:

        for i in range(len(h.get("sizes", []))):

            rows.append({

                "Slip No": h.get("slip_no", ""),
                "Date": h.get("date", ""),
                "Party": h.get("party", ""),
                "Address": h.get("address", ""),
                "Cloth": h.get("cloth", ""),
                "School": h.get("school", ""),
                "Item": h.get("item", ""),
                "Size": h.get("sizes", [])[i] if i < len(h.get("sizes", [])) else "",
                "Qty": h.get("qtys", [])[i] if i < len(h.get("qtys", [])) else "",
                "Meter": h.get("meters", [])[i] if i < len(h.get("meters", [])) else "",
                "Total Qty": h.get("total_qty", ""),
                "Total Meter": h.get("total_meter", ""),
                "Remark": h.get("remark", ""),
                "Status": h.get("status", "")
            })

    df = pd.DataFrame(rows)

    # Slip No ascending
    df = df.sort_values(by="Slip No", ascending=True)

    file_name = os.path.join(BASE_DIR, "Cutting_Slip_History.xlsx")

    df.to_excel(file_name, index=False)

    from flask import send_file
    import time

    time.sleep(1)

    return send_file(
        file_name,
        as_attachment=True,
        download_name="Cutting_Slip_History.xlsx"
    )

@app.route("/download_pdf/<slip_no>")
def download_pdf(slip_no):

    history = load_history()

    slip = next(
        (
            s for s in history
            if str(s.get("slip_no")) == str(slip_no)
        ),
        None
    )

    if not slip:
        return "Slip not found"

    file_name = f"Slip_{slip_no}.pdf"

    pdf = SimpleDocTemplate(
        file_name,
        pagesize=letter
    )

    elements = []

    title = Paragraph(
        f"<b>SARVODAY STORES</b><br/>CUTTING SLIP",
        getSampleStyleSheet()['Title']
    )

    elements.append(title)
    elements.append(Spacer(1,12))

    details = f"""
    <b>Slip No:</b> {slip.get('slip_no','')}<br/>
    <b>Date:</b> {slip.get('date','')}<br/>
    <b>Party:</b> {slip.get('party','')}<br/>
    <b>Address:</b> {slip.get('address','')}<br/>
    <b>Cloth:</b> {slip.get('cloth','')}<br/>
    <b>School:</b> {slip.get('school','')}<br/>
    <b>Item:</b> {slip.get('item','')}<br/>
    """

    elements.append(
        Paragraph(
            details,
            getSampleStyleSheet()['BodyText']
        )
    )

    elements.append(Spacer(1,12))

    data = [["Size","Qty","Meter"]]

    sizes = slip.get("sizes",[])
    qtys = slip.get("qtys",[])
    meters = slip.get("meters",[])

    for i in range(len(sizes)):

        data.append([

            sizes[i],

            qtys[i],

            f"{float(meters[i]):.2f}"
        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND',(0,0),(-1,0),colors.darkblue),

        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')

    ]))

    elements.append(table)

    elements.append(Spacer(1,12))

    remark_text = str(
        slip.get("remark", "")
    ).replace("\n", "<br/>")

    totals = f"""
    <b>Total Qty:</b> {slip.get('total_qty',0)}<br/>
    <b>Total Meter:</b> {slip.get('total_meter',0)}<br/><br/>
    <b>Remark:</b><br/><br/>{remark_text}
    """

    elements.append(
        Paragraph(
            totals,
            getSampleStyleSheet()['BodyText']
        )
    )

    pdf.build(elements)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route("/update_party", methods=["POST"])
def update_party():

    data = request.json

    old_name = data.get("old_name")
    new_name = data.get("new_name")
    address = data.get("address")

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cursor = conn.cursor()

    # UPDATE PARTY MASTER

    cursor.execute(
        """
        UPDATE parties
        SET
            party_name = ?,
            party_address = ?
        WHERE party_name = ?
        """,
        (
            new_name,
            address,
            old_name
        )
    )

    # UPDATE OLD SLIPS HISTORY

    # UPDATE OLD SLIPS HISTORY

    cursor.execute(
        """
        UPDATE slips
        SET
            party = ?,
            address = ?
        WHERE TRIM(UPPER(party)) = TRIM(UPPER(?))
        """,
        (
            new_name,
            address,
            old_name
        )
    )

    conn.commit()

    conn.close()

    return jsonify({
        "status": "success"
    })



@app.route("/delete_party", methods=["POST"])
def delete_party():

    data = request.json

    party_name = data.get("party_name", "").strip()

    import sqlite3

    conn = sqlite3.connect(
    os.path.join(BASE_DIR, "cutting_slip.db")
)

    cursor = conn.cursor()

    # CHECK PARTY USED IN SLIPS

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM slips
        WHERE TRIM(party)=?
        """,
        (party_name,)
    )

    used_count = cursor.fetchone()[0]

    # BLOCK DELETE

    if used_count > 0:

        conn.close()

        return jsonify({
            "status": "error",
            "message": "Party already used in slips"
        })

    # DELETE PARTY

    cursor.execute(
        """
        DELETE FROM parties
        WHERE TRIM(party_name)=?
        """,
        (party_name,)
    )

    deleted_rows = cursor.rowcount

    conn.commit()

    conn.close()

    if deleted_rows > 0:

        return jsonify({
            "status": "success"
        })

    else:

        return jsonify({
            "status": "error",
            "message": "Party not found"
        })

import webbrowser
import threading

def open_browser():

    webbrowser.open(
        "http://127.0.0.1:5000"
    )

if __name__ == "__main__":

    threading.Timer(
        1.5,
        open_browser
    ).start()

    app.run(debug=False)