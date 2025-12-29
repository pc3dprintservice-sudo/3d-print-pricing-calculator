from flask import Flask, render_template, request
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =====================
# CONFIG
# =====================
IS_PRO = True  # Toggle later

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =====================
# MAIN CALCULATOR
# =====================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        currency = request.form.get("currency", "R")
        vat_enabled = "vat" in request.form

        description = request.form.get("description", "").strip()
        if not description:
            description = "3D Printed Item"

        grams = float(request.form.get("grams", 0))
        cost_per_kg = float(request.form.get("cost_per_kg", 0))
        hours = float(request.form.get("hours", 0))
        hourly_rate = float(request.form.get("hourly_rate", 0))

        power_watts = float(request.form.get("power_watts", 0))
        electricity_rate = float(request.form.get("electricity_rate", 0))

        labour_hours = float(request.form.get("labour_hours", 0))
        labour_rate = float(request.form.get("labour_rate", 0))

        margin = float(request.form.get("margin", 0)) / 100

        filament_cost = (grams / 1000) * cost_per_kg
        machine_cost = hours * hourly_rate
        electricity_cost = (power_watts / 1000) * hours * electricity_rate
        labour_cost = labour_hours * labour_rate

        total_cost = filament_cost + machine_cost + electricity_cost + labour_cost
        selling_price = total_cost * (1 + margin)

        vat_amount = selling_price * 0.15 if vat_enabled else None
        final_price = selling_price + vat_amount if vat_amount else selling_price
        profit = selling_price - total_cost

        business_name = request.form.get("business_name", "Your business name here")
        logo_file = request.files.get("logo")
        logo_url = None

        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            logo_file.save(path)
            logo_url = f"/{path}"

        def money(v):
            return f"{currency} {v:,.2f}"

        result = {
            "description": description,
            "filament_cost": money(filament_cost),
            "machine_cost": money(machine_cost),
            "electricity_cost": money(electricity_cost),
            "labour_cost": money(labour_cost),
            "total_cost": money(total_cost),
            "selling_price": money(selling_price),
            "vat_amount": money(vat_amount) if vat_amount else None,
            "final_price": money(final_price),
            "profit": money(profit),
            "margin": round(margin * 100, 2),
            "vat_enabled": vat_enabled,
            "business_name": business_name,
            "logo_url": logo_url,
        }

    return render_template("index.html", result=result, is_pro=IS_PRO)


# =====================
# INVOICE
# =====================
@app.route("/quote")
def quote():
    data = request.args
    now = datetime.now()

    invoice_ref = f"INV-{now.strftime('%Y%m%d-%H%M%S')}"

    return render_template(
        "quote.html",
        data=data,
        date=now.strftime("%d %b %Y"),
        invoice_ref=invoice_ref,
        is_pro=IS_PRO,
    )


# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
