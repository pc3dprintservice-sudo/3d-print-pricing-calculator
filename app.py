from flask import Flask, render_template, request
import uuid
import os

app = Flask(__name__)


# =========================
# SAFE FLOAT HELPER
# =========================
def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# =========================
# SHARED CALCULATION LOGIC
# =========================
def calculate(form, is_pro):
    currency = form.get("currency", "R")

    business_name = form.get("business_name", "")
    description = form.get("description", "")
    quantity = int(form.get("quantity", 1) or 1)

    filament_type = form.get("filament_type", "") if is_pro else ""
    banking_details = form.get("banking_details", "") if is_pro else ""

    grams = to_float(form.get("grams"))
    cost_per_kg = to_float(form.get("cost_per_kg"))
    hours = to_float(form.get("hours"))
    hourly_rate = to_float(form.get("hourly_rate"))
    power_watts = to_float(form.get("power_watts"))
    electricity_rate = to_float(form.get("electricity_rate"))
    labour_hours = to_float(form.get("labour_hours"))
    labour_rate = to_float(form.get("labour_rate"))
    margin = to_float(form.get("margin")) / 100
    waste = to_float(form.get("waste_percent")) / 100

    filament_cost = (grams / 1000) * cost_per_kg
    machine_cost = hours * hourly_rate
    electricity_cost = (power_watts / 1000) * hours * electricity_rate
    labour_cost = labour_hours * labour_rate

    internal_cost = (filament_cost + machine_cost + electricity_cost + labour_cost)
    internal_cost *= (1 + waste)

    unit_price = internal_cost / (1 - margin) if margin < 1 else internal_cost
    total_price = unit_price * quantity

    return {
        "invoice_number": str(uuid.uuid4())[:8].upper(),
        "business_name": business_name,
        "description": description,
        "filament_type": filament_type,
        "banking_details": banking_details,
        "quantity": quantity,

        "unit_price": f"{currency}{unit_price:,.2f}",
        "total_price": f"{currency}{total_price:,.2f}",

        "filament_cost": f"{currency}{filament_cost:,.2f}",
        "machine_cost": f"{currency}{machine_cost:,.2f}",
        "electricity_cost": f"{currency}{electricity_cost:,.2f}",
        "labour_cost": f"{currency}{labour_cost:,.2f}",
        "internal_cost": f"{currency}{internal_cost:,.2f}",
    }


# =========================
# FREE VERSION
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        result = calculate(request.form, is_pro=False)

    return render_template(
        "index.html",
        result=result,
        is_pro=False,
        currency=request.form.get("currency", "R"),
        form=request.form
    )


# =========================
# PRO VERSION (PRIVATE LINK)
# =========================
@app.route("/access-9f3kA2", methods=["GET", "POST"])
def access_pro():
    result = None

    if request.method == "POST":
        result = calculate(request.form, is_pro=True)

    return render_template(
        "index.html",
        result=result,
        is_pro=True,
        currency=request.form.get("currency", "R"),
        form=request.form
    )


# =========================
# FREE vs PRO PAGE
# =========================
@app.route("/pricing")
def pricing():
    return render_template("pricing.html", is_pro=False)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
