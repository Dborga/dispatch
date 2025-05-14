from flask import Flask, render_template, request
import smartsheet
from datetime import datetime

app = Flask(__name__)

# Smartsheet setup
API_TOKEN = "6XvWiRPheYeVwnD1PBYtpQf3POKrLafvQYniM"
WORKSPACE_NAME = "Canada Manual Dispatches"
smartsheet_client = smartsheet.Smartsheet(API_TOKEN)
smartsheet_client.errors_as_exceptions(True)

def get_workspace_id_by_name(name):
    workspaces = smartsheet_client.Workspaces.list_workspaces().data
    for ws in workspaces:
        if ws.name == name:
            return ws.id
    return None

def get_existing_sheet_id(month_name):
    workspace_id = get_workspace_id_by_name(WORKSPACE_NAME)
    sheets = smartsheet_client.Workspaces.get_workspace(workspace_id).sheets
    for sheet in sheets:
        if sheet.name == month_name:
            return sheet.id
    raise Exception(f"No sheet found for {month_name}. Please create it manually in Smartsheet.")

def add_row_to_sheet(sheet_id, form):
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    col_map = {col.title: col.id for col in sheet.columns}

    new_row = smartsheet.models.Row()
    new_row.to_top = True
    new_row.cells = [
        {"column_id": col_map["Name"], "value": form.get("shipto_name")},
        {"column_id": col_map["Address"], "value": form.get("site_address")},
        {"column_id": col_map["Company"], "value": form.get("customer_name")},
        {"column_id": col_map["Shipto"], "value": ""},
        {"column_id": col_map["Type"], "value": form.get("product")},
        {"column_id": col_map["Manual Dispatch Name"], "value": form.get("order_number")},
        {"column_id": col_map["Order Made to Replace Manual?"], "value": ""},
        {"column_id": col_map["PO"], "value": form.get("corporate_po") or ""},
        {"column_id": col_map["Date"], "value": form.get("delivery_date")},
    ]

    smartsheet_client.Sheets.add_rows(sheet_id, [new_row])

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/result', methods=['POST'])
def result():
    form = request.form
    delivery_date_raw = form.get("delivery_date")
    month_str = datetime.strptime(delivery_date_raw, "%Y-%m-%d").strftime("%B %Y")
    formatted_date = datetime.strptime(delivery_date_raw, "%Y-%m-%d").strftime("%m/%d/%Y")

    terminal = form.get("terminal")
    container = form.get("container")

    # Supplier logic
    if terminal == "943 Delson MCU DEF INV 180 Theberge St Delson, Quebec, Canada J5B 1X2":
        supplier = "Mansfield of Canada ULC"
    elif terminal == "Niagara Falls ON-Oleo Energies 5800 Thorold Stone Rd Niagara Falls, Ontario, Canada L2J1A2":
        supplier = "Oleo Energies Inc" if container == "Packaged" else "Mansfield of Canada ULC"
    elif terminal == "Ponoka AB-CBluO 253020 Twp Rd 432 Ponoka, Alberta, Canada T4J 1R2":
        supplier = "CBluO (DBA)"
    elif terminal == "Longueuil QC-Crevier 2320 De La Metropole Longueuil, Quebec, Canada J46 1E6":
        supplier = "Crevier Lubricant Inc"
    elif terminal == "Kitchener ON-FS Partners 1 Chandaria Place Unit 7 Kitchener, Ontario, Canada N0M1X0":
        supplier = "FS Partners"
    else:
        supplier = "N/A"

    sheet_id = get_existing_sheet_id(month_str)
    add_row_to_sheet(sheet_id, form)

    data = {
        "dispatch_comments": form.get("dispatch_comments"),
        "customer_name": form.get("customer_name"),
        "shipto_name": form.get("shipto_name"),
        "site_address": form.get("site_address"),
        "site_contact": "N/A",
        "deliveries": [
            {
                "order_number": form.get("order_number"),
                "delivery_number": form.get("delivery_number"),
                "brand": form.get("brand"),
                "product": form.get("product"),
                "quantity": form.get("quantity"),
                "uom": "L",
                "total_weight": "N/A",
                "terminal": terminal,
                "supplier": supplier,
                "type": form.get("product"),
                "loading_number": "N/A",
                "corporate_po": form.get("corporate_po"),
                "delivery_date": formatted_date,
                "delivery_day": datetime.strptime(delivery_date_raw, "%Y-%m-%d").strftime("%A"),
                "delivery_window": "N/A",
                "tank": "N/A"
            }
        ]
    }

    return render_template("result.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)









