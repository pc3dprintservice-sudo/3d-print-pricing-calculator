from flask import Flask, render_template, request
import uuid
import os

app = Flask(__name__)

# =========================
# MODE TOGGLE
# =========================
IS_PRO = False   # Change to False for Free mode


# =========================
# MAIN CALCULATOR
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        # -------- Basic inputs --------
        business_name = request.form.get("business_name", "")
        description = request.form.get("description", "")
        currency = request.form.get("currency", "R")
        quantity = int(request.form.get("quantity", 1))

        # -------- Pro-only inputs --------
        filament_type = request.form.get("filament_type", "") if IS_PRO else ""
        banking_details = request.form.get("banking_details", "") if IS_PRO else ""

        # -------- Cost inputs --------
        grams = float(request.form.get("grams", 0))
        cost_per_kg = float(request.form.get("cost_per_kg", 0))
        hours = float(request.form.get("hours", 0))
        hourly_rate = float(request.form.get("hourly_rate", 0))
        power_watts = float(request.form.get("power_watts", 0))
        electricity_rate = float(request.form.get("electricity_rate", 0))
        labour_hours = float(request.form.get("labour_hours", 0))
        labour_rate = float(request.form.get("labour_rate", 0))
        margin = float(request.form.get("margin", 0)) / 100
        waste = float(request.form.get("waste_percent", 0)) / 100

        # -------- Calculations --------
        filament_cost = (grams / 1000) * cost_per_kg
        machine_cost = hours * hourly_rate
        electricity_cost = (power_watts / 1000) * hours * electricity_rate
        labour_cost = labour_hours * labour_rate

        internal_cost = (filament_cost + machine_cost + electricity_cost + labour_cost)
        internal_cost *= (1 + waste)

        unit_price = internal_cost / (1 - margin) if margin < 1 else internal_cost
        total_price = unit_price * quantity

        # -------- Result payload --------
        result = {
            "invoice_number": str(uuid.uuid4())[:8].upper(),
            "business_name": business_name,
            "description": description,
            "filament_type": filament_type,
            "banking_details": banking_details,
            "quantity": quantity,

            "unit_price": f"{currency}{unit_price:,.2f}",
            "total_price": f"{currency}{total_price:,.2f}",

            # Internal costs (Pro only display)
            "filament_cost": f"{currency}{filament_cost:,.2f}",
            "machine_cost": f"{currency}{machine_cost:,.2f}",
            "electricity_cost": f"{currency}{electricity_cost:,.2f}",
            "labour_cost": f"{currency}{labour_cost:,.2f}",
            "internal_cost": f"{currency}{internal_cost:,.2f}",
        }

    return render_template("index.html", result=result, is_pro=IS_PRO)


# =========================
# FREE vs PRO PAGE
# =========================
@app.route("/pricing")
def pricing():
    return render_template("pricing.html", is_pro=IS_PRO)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
