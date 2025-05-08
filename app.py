from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/result', methods=['POST'])
def result():
    form = request.form
    data = {
        "dispatch_comments": form.get("dispatch_comments"),
        "customer_name": form.get("customer_name"),
        "shipto_name": form.get("shipto_name"),
        "site_address": form.get("site_address"),
        "deliveries": []
    }

    for i in range(6):
        suffix = f"_{i}" if i > 0 else ""
        if form.get(f"product{suffix}") or form.get(f"corporate_po{suffix}"):
            raw_date = form.get(f"delivery_date{suffix}")
            delivery_date = ""
            delivery_day = ""
            if raw_date:
                try:
                    parsed = datetime.strptime(raw_date, "%Y-%m-%d")
                    delivery_date = parsed.strftime("%m/%d/%Y")
                    delivery_day = parsed.strftime("%A")
                except ValueError:
                    pass

            terminal = form.get(f"terminal{suffix}", "")
            container = form.get(f"container{suffix}", "")
            supplier = ""

            if "943 Delson" in terminal:
                supplier = "Mansfield of Canada ULC"
            elif "Niagara Falls" in terminal:
                supplier = "Mansfield of Canada ULC" if container == "Diesel Exhaust Fluid 1-1250" else "Oleo Energies Inc"
            elif "Ponoka" in terminal:
                supplier = "CBluO (DBA)"
            elif "Longueuil" in terminal:
                supplier = "Crevier Lubricant Inc"
            elif "Kitchener" in terminal:
                supplier = "FS Partners"

            delivery = {
                "order_number": form.get("order_number"),
                "delivery_number": form.get("delivery_number"),
                "brand": form.get(f"brand{suffix}"),
                "product": form.get(f"product{suffix}"),
                "quantity": form.get(f"quantity{suffix}"),
                "corporate_po": form.get(f"corporate_po{suffix}"),
                "delivery_window": form.get(f"delivery_window{suffix}", ""),  # Optional
                "terminal": terminal,
                "supplier": supplier,
                "delivery_date": delivery_date,
                "delivery_day": delivery_day,
                "uom": "Liter",
                "total_weight": "",
                "type": "",
                "loading_number": "",
                "tank": "1250 - Liter - DEF - AST - PUMP REQUIRED"
            }

            data["deliveries"].append(delivery)

    return render_template("result.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)






