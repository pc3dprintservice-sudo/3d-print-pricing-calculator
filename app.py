from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}

    if request.method == "POST":
        grams = float(request.form["grams"])
        cost_per_kg = float(request.form["cost_per_kg"])
        hours = float(request.form["hours"])
        hourly_rate = float(request.form["hourly_rate"])
        margin = float(request.form["margin"]) / 100

        filament_cost = (grams / 1000) * cost_per_kg
        machine_cost = hours * hourly_rate
        total_cost = filament_cost + machine_cost
        selling_price = total_cost / (1 - margin)
        profit = selling_price - total_cost

        result = {
            "total_cost": round(total_cost, 2),
            "selling_price": round(selling_price, 2),
            "profit": round(profit, 2),
            "margin": round(margin * 100, 2)
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
