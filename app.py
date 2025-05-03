from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')  # Uses your existing form.html

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
        # Only add if there's a product or PO field
        if form.get(f"product{suffix}") or form.get(f"corporate_po{suffix}"):
            delivery = {
                "order_number": form.get("order_number"),
                "delivery_number": form.get("delivery_number"),
                "brand": form.get(f"brand{suffix}"),
                "product": form.get(f"product{suffix}"),
                "quantity": form.get(f"quantity{suffix}"),
                "corporate_po": form.get(f"corporate_po{suffix}"),
                "delivery_window": form.get(f"delivery_window{suffix}"),
                "terminal": form.get(f"terminal{suffix}"),
                "supplier": "",
                "delivery_date": "",
                "delivery_day": ""
            }

            raw_date = form.get(f"delivery_date{suffix}")
            if raw_date:
                try:
                    parsed = datetime.strptime(raw_date, "%Y-%m-%d")
                    delivery["delivery_date"] = parsed.strftime("%m/%d/%Y")
                    delivery["delivery_day"] = parsed.strftime("%A")
                except ValueError:
                    pass

            terminal = delivery["terminal"]
            container = form.get(f"container{suffix}")

            if "943 Delson MCU DEF INV" in terminal:
                delivery["supplier"] = "Mansfield of Canada ULC"
            elif "Niagara Falls ON-Oleo Energies" in terminal:
                if container == "Diesel Exhaust Fluid 1-1250":
                    delivery["supplier"] = "Mansfield of Canada ULC"
                elif container == "Packaged":
                    delivery["supplier"] = "Oleo Energies Inc"
            elif "Ponoka AB-CBluO" in terminal:
                delivery["supplier"] = "CBluO (DBA)"
            elif "Longueuil QC-Crevier" in terminal:
                delivery["supplier"] = "Crevier Lubricant Inc"
            elif "Kitchener ON-FS Partners" in terminal:
                delivery["supplier"] = "FS Partners"

            data["deliveries"].append(delivery)

    return render_template("result.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)




