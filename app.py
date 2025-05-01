from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/result', methods=['POST'])
def result():
    data = request.form.to_dict()

    # Format delivery date to MM/DD/YYYY
    if 'delivery_date' in data:
        try:
            parsed_date = datetime.strptime(data['delivery_date'], "%Y-%m-%d")
            data['delivery_date'] = parsed_date.strftime("%m/%d/%Y")
        except ValueError:
            pass

    # Determine supplier based on terminal and container
    terminal = data.get("terminal", "")
    container = data.get("container", "")
    
    if "943 Delson MCU DEF INV" in terminal:
        data["supplier"] = "Mansfield of Canada ULC"
    elif "Niagara Falls ON-Oleo Energies" in terminal:
        if container == "Diesel Exhaust Fluid 1-1250":
            data["supplier"] = "Mansfield of Canada ULC"
        elif container == "Packaged":
            data["supplier"] = "Oleo Energies Inc"
    elif "Ponoka AB-CBluO" in terminal:
        data["supplier"] = "CBluO (DBA)"
    elif "Longueuil QC-Crevier" in terminal:
        data["supplier"] = "Crevier Lubricant Inc"
    elif "Kitchener ON-FS Partners" in terminal:
        data["supplier"] = "FS Partners"
    else:
        data["supplier"] = ""

    return render_template('result.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

