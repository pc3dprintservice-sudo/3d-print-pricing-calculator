from flask import Flask, render_template, request
IS_PRO = True  # ← change to True to enable Pro features
app = Flask(__name__)
import datetime
def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
    
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        # Meta
        invoice_number = datetime.datetime.now().strftime("INV-%Y%m%d-%H%M%S")
        business_name = request.form.get("business_name", "").strip()
        description = request.form.get("description", "").strip()
        filament_type = request.form.get("filament_type", "")
        currency = request.form.get("currency", "R")
        vat_enabled = request.form.get("vat") == "on"

        # Inputs
        grams = to_float(request.form.get("grams"))
        cost_per_kg = to_float(request.form.get("cost_per_kg"))
        hours = to_float(request.form.get("hours"))
        hourly_rate = to_float(request.form.get("hourly_rate"))
        power_watts = to_float(request.form.get("power_watts"))
        electricity_rate = to_float(request.form.get("electricity_rate"))
        labour_hours = to_float(request.form.get("labour_hours"))
        labour_rate = to_float(request.form.get("labour_rate"))
        margin = to_float(request.form.get("margin")) / 100
        waste_percent = to_float(request.form.get("waste_percent")) / 100

        try:
            quantity = int(request.form.get("quantity", 1))
        except ValueError:
            quantity = 1

        # Costs
        filament_cost = (grams / 1000) * cost_per_kg
        machine_cost = hours * hourly_rate
        electricity_cost = (power_watts / 1000) * hours * electricity_rate
        labour_cost = labour_hours * labour_rate

        variable_cost = filament_cost + electricity_cost
        adjusted_variable_cost = variable_cost * (1 + waste_percent)

        fixed_cost = machine_cost + labour_cost
        total_cost = (adjusted_variable_cost * quantity) + fixed_cost

        selling_price = total_cost / (1 - margin) if margin < 1 else 0
        price_per_unit = selling_price / quantity if quantity else 0

        vat_amount = selling_price * 0.15 if vat_enabled else 0
        final_price = selling_price + vat_amount

        result = {
            "invoice_number": invoice_number,
            "business_name": business_name,
            "description": description,
            "filament_type": filament_type,

            "filament_cost": f"{currency}{filament_cost:.2f}",
            "machine_cost": f"{currency}{machine_cost:.2f}",
            "electricity_cost": f"{currency}{electricity_cost:.2f}",
            "labour_cost": f"{currency}{labour_cost:.2f}",
            "waste_percent": f"{waste_percent * 100:.0f}%",
            "total_cost": f"{currency}{total_cost:.2f}",

            "price_per_unit": f"{currency}{price_per_unit:.2f}",
            "final_price": f"{currency}{final_price:.2f}",
            "vat_amount": f"{currency}{vat_amount:.2f}",
            "vat_enabled": vat_enabled,
            "quantity": quantity
        }

    return render_template(
    "index.html",
    result=result,
    is_pro=IS_PRO
)

if __name__ == "__main__":
    app.run(debug=True)
