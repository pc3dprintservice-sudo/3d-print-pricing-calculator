from flask import Flask, render_template, request
from datetime import datetime
IS_PRO = False  # change to True later for Pro users


app = Flask(__name__, template_folder="templates")


def money(value, symbol):
    return f"{symbol} {value:,.2f}"


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        currency = request.form.get("currency", "R")
        vat_enabled = request.form.get("vat") == "on"

        grams = float(request.form["grams"])
        cost_per_kg = float(request.form["cost_per_kg"])
        hours = float(request.form["hours"])
        hourly_rate = float(request.form["hourly_rate"])

        power_watts = float(request.form.get("power_watts", 0) or 0)
        electricity_rate = float(request.form.get("electricity_rate", 0) or 0)

        labour_hours = float(request.form.get("labour_hours", 0) or 0)
        labour_rate = float(request.form.get("labour_rate", 0) or 0)

        margin = float(request.form.get("margin", 0)) / 100

        filament_cost = (grams / 1000) * cost_per_kg
        machine_cost = hours * hourly_rate
        electricity_cost = (power_watts / 1000) * hours * electricity_rate
        labour_cost = labour_hours * labour_rate

        total_cost = filament_cost + machine_cost + electricity_cost + labour_cost
        selling_price = total_cost / (1 - margin) if margin < 1 else 0
        profit = selling_price - total_cost

        vat_rate = 0.15
        vat_amount = selling_price * vat_rate if vat_enabled else 0
        final_price = selling_price + vat_amount

        result = {
            "filament_cost": money(filament_cost, currency),
            "machine_cost": money(machine_cost, currency),
            "electricity_cost": money(electricity_cost, currency),
            "labour_cost": money(labour_cost, currency),

            "total_cost": money(total_cost, currency),

            "selling_price": money(selling_price, currency),
            "vat_amount": money(vat_amount, currency),
            "final_price": money(final_price, currency),

            "profit": money(profit, currency),
            "margin": round(margin * 100, 2),
            "vat_enabled": vat_enabled
        }

    return render_template("index.html", result=result)


@app.route("/quote")
def quote():
    data = request.args
    now = datetime.now()

    quote_ref = f"INV-{now.strftime('%Y%m%d-%H%M%S')}"

    return render_template(
        "quote.html",
        data=data,
        date=now.strftime("%d %b %Y"),
        quote_ref=quote_ref,
        is_pro=IS_PRO,
        business_name="Your Business Name",
        logo_url="/static/logo.png"
    )
  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
