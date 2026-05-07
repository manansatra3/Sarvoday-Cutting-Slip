from flask import Flask, render_template, request, redirect
import json
import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "slip_history.json")


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_history(data):
    history = load_history()
    history.append(data)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

from openpyxl import load_workbook

def load_party_data():
    file_path = os.path.join(BASE_DIR, "parties.xlsx")
    party_list = []

    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
            if row[0]:
                party_list.append(str(row[0]))

    return party_list


def load_item_data():
    file_path = os.path.join(BASE_DIR, "Item Name.xlsx")
    items = set()

    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[0]:
                items.add(str(row[0]).strip())

    return sorted(list(items))

def get_next_slip_no():
    history = load_history()
    return len(history) + 1

from openpyxl import load_workbook

import pandas as pd

def load_party_details():

    file_path = os.path.join(BASE_DIR, "Master Data.xlsx")

    party_data = {}
    school_list = []
    cloth_list = []

    if os.path.exists(file_path):

        df = pd.read_excel(file_path)

        for _, row in df.iterrows():

            party = str(row.get("Party Name", "")).strip()
            address = str(row.get("Address", "")).strip()
            school = str(row.get("School Name", "")).strip()
            cloth = str(row.get("Cloth", "")).strip()

            # Party + Address
            if party and party != "nan":
                party_data[party] = address

            # School List
            if school and school != "nan":
                if school not in school_list:
                    school_list.append(school)

            # Cloth List
            if cloth and cloth != "nan":
                if cloth not in cloth_list:
                    cloth_list.append(cloth)

    return {
        "party_data": party_data,
        "school_list": sorted(school_list),
        "cloth_list": sorted(cloth_list)
    }

def load_size_map():
    file_path = os.path.join(BASE_DIR, "Item Name.xlsx")
    size_map = {}

    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):

            if not row or not row[0] or not row[1]:
                continue

            item = str(row[0]).strip()   # Name
            size = str(row[1]).strip()   # Size

            if item not in size_map:
                size_map[item] = []

            size_map[item].append(size)

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
                request.form.get("date"),
                "%Y-%m-%d"
            ).strftime("%d-%m-%Y"),
            "party": request.form.get("party"),
            "address": request.form.get("address"),
            "cloth": request.form.get("cloth"),
            "school": request.form.get("school"),
            "item": request.form.get("item"),
            "sizes": request.form.getlist("size[]"),
            "qtys": request.form.getlist("qty[]"),
            "meters": request.form.getlist("meter[]"),
            "total_qty": request.form.get("total_qty"),
            "total_meter": request.form.get("total_meter")
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
        size_map=size_map
    )
    

if __name__ == "__main__":
    app.run(debug=True)
