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

def add_row_to_sheet(sheet_id, form, index_suffix=""):
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    col_map = {col.title: col.id for col in sheet.columns}

    def get_field(name):
        return form.get(f"{name}{index_suffix}") or ""

    new_row = smartsheet.models.Row()
    new_row.to_top = True
    new_row.cells = [
        {"column_id": col_map["Name"], "value": form.get("shipto_name")},
        {"column_id": col_map["Address"], "value": form.get("site_address")},
        {"column_id": col_map["Company"], "value": form.get("customer_name")},
        {"column_id": col_map["Shipto"], "value": ""},
        {"column_id": col_map["Type"], "value": get_field("product")},
        {"column_id": col_map["Manual Dispatch Name"], "value": form.get("order_number")},
        {"column_id": col_map["Order Made to Replace Manual?"], "value": ""},
        {"column_id": col_map["PO"], "value": get_field("corporate_po")},
        {"column_id": col_map["Date"], "value": get_field("delivery_date")},
    ]

    smartsheet_client.Sheets.add_rows(sheet_id, [new_row])

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/result', methods=['POST'])
def result():
    form = request.form

    order_number = form.get("order_number")
    delivery_number = form.get("delivery_number")
    delivery_date_raw = form.get("delivery_date")
    formatted_date = datetime.strptime(delivery_date_raw, "%Y-%m-%d").strftime("%m/%d/%Y")
    delivery_day = datetime.strptime(delivery_date_raw, "%Y-%m-%d").strftime("%A")
    month_str = datetime.strptime(delivery_date_raw, "%Y-%m-%d").strftime("%B %Y")
    sheet_id = get_existing_sheet_id(month_str)

    data = {
        "dispatch_comments": form.get("dispatch_comments"),
        "customer_name": form.get("customer_name"),
        "shipto_name": form.get("shipto_name"),
        "site_address": form.get("site_address"),
        "site_contact": "N/A",
        "deliveries": []
    }

    # Collect all product values for "Type" column
    all_products = []

    for i in range(6):
        suffix = f"_{i}" if i > 0 else ""
        product = form.get(f"product{suffix}")
        if not product:
            continue

        all_products.append(product)
        terminal = form.get(f"terminal{suffix}")
        container = form.get(f"container{suffix}")

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

        data["deliveries"].append({
            "order_number": order_number,
            "delivery_number": delivery_number,
            "brand": form.get(f"brand{suffix}"),
            "product": product,
            "quantity": form.get(f"quantity{suffix}"),
            "uom": "L",
            "total_weight": "N/A",
            "terminal": terminal,
            "supplier": supplier,
            "type": product,
            "loading_number": "N/A",
            "corporate_po": form.get(f"corporate_po{suffix}"),
            "delivery_date": formatted_date,
            "delivery_day": delivery_day,
            "delivery_window": "N/A",
            "tank": "N/A"
        })

    # Build "Type" string for Smartsheet like "Def Jugs and Def Drums"
    combined_type = " and ".join(all_products)

    # Only one row needs to be added to Smartsheet, but with combined Type
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    col_map = {col.title: col.id for col in sheet.columns}

    new_row = smartsheet.models.Row()
    new_row.to_top = True
    new_row.cells = [
        {"column_id": col_map["Name"], "value": form.get("shipto_name")},
        {"column_id": col_map["Address"], "value": form.get("site_address")},
        {"column_id": col_map["Company"], "value": form.get("customer_name")},
        {"column_id": col_map["Shipto"], "value": ""},
        {"column_id": col_map["Type"], "value": combined_type},
        {"column_id": col_map["Manual Dispatch Name"], "value": order_number},
        {"column_id": col_map["Order Made to Replace Manual?"], "value": ""},
        {"column_id": col_map["PO"], "value": form.get("corporate_po") or ""},
        {"column_id": col_map["Date"], "value": delivery_date_raw},
    ]

    smartsheet_client.Sheets.add_rows(sheet_id, [new_row])

    return render_template("result.html", data=data)


if __name__ == '__main__':
    app.run(debug=True)










