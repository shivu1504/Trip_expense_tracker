from flask import Flask, render_template, request, redirect

from database import (
    get_trips,
    get_members,
    add_trip,
    get_trip,
    get_trip_by_code,
    join_trip,
    add_member,
    get_expenses,
    add_expense,
    add_expense_participant,
    get_split_totals,
    get_total_paid
)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        trip_name = request.form["trip_name"].strip()

        member_names = request.form.getlist("member_names")

        member_names = [
            name.strip()
            for name in member_names
            if name.strip()
        ]

        if trip_name and member_names:

            trip_id = add_trip(trip_name)

            for member_name in member_names:
                add_member(trip_id, member_name)

            return redirect(f"/trip/{trip_id}")

    trips = get_trips()

    return render_template(
        "index.html",
        trips=trips
    )

@app.route("/add-expense")
def add_expense_page():

    trips = get_trips()

    if not trips:
        return redirect("/")

    last_trip_id = trips[0]["id"]

    return redirect(
        f"/manage-expenses/{last_trip_id}"
    )

@app.route("/delete-member/<int:member_id>", methods=["POST"])
def delete_member_route(member_id):

    from database import delete_member

    delete_member(member_id)

    return redirect(request.referrer)

@app.route("/trip/<int:trip_id>")
def trip(trip_id):

    trip = get_trip(trip_id)

    members = get_members(trip_id)

    expenses = get_expenses(trip_id)

    split_totals = get_split_totals(trip_id)

    total_paid = get_total_paid(trip_id)

    return render_template(
        "trip.html",
        trip=trip,
        members=members,
        expenses=expenses,
        split_totals=split_totals,
        total_paid=total_paid
    )


@app.route("/trip-memory/<int:trip_id>")
def trip_memory(trip_id):

    trip = get_trip(trip_id)

    return render_template(
        "trip_memory.html",
        trip=trip
    )


@app.route("/complete-trip/<int:trip_id>")
def complete_trip(trip_id):

    trip = get_trip(trip_id)

    return render_template(
        "complete_trip.html",
        trip=trip
    )

@app.route("/join-trip", methods=["POST"])
def join_trip_route():

    member_name = request.form["member_name"].strip()
    trip_code = request.form["trip_code"].strip().upper()

    if not member_name or not trip_code:
        trips = get_trips()

        return render_template(
            "index.html",
            trips=trips,
            join_error="Please enter your name and Trip Code."
        )

    trip = get_trip_by_code(trip_code)

    if not trip:
        trips = get_trips()

        return render_template(
            "index.html",
            trips=trips,
            join_error="Trip Code not found. Please check the code and try again."
        )

    join_trip(trip["id"], member_name)

    return redirect(f"/trip/{trip['id']}")



@app.route("/manage-members/<int:trip_id>", methods=["GET", "POST"])
def manage_members(trip_id):

    if request.method == "POST":

        member_name = request.form["member_name"].strip()

        if member_name:
            add_member(trip_id, member_name)

        return redirect(f"/manage-members/{trip_id}")

    trip = get_trip(trip_id)

    members = get_members(trip_id)

    return render_template(
        "manage_members.html",
        trip=trip,
        members=members
    )

@app.route("/manage-expenses/<int:trip_id>", methods=["GET", "POST"])
def manage_expenses(trip_id):

    if request.method == "POST":

        expense_title = request.form["expense_title"].strip()
        expense_amount = float(request.form["expense_amount"])
        expense_paid_by = request.form["expense_paid_by"]
        expense_date = request.form["expense_date"]
      

        split_type = request.form["split_type"]

        excluded_members = request.form.getlist(
            "excluded_members"
        )

        if expense_title and expense_amount and expense_paid_by and expense_date:

            members = get_members(trip_id)

            if split_type == "all":

                participants = members

            else:

                participants = [
                    member
                    for member in members
                    if str(member["id"]) not in excluded_members
                ]

            if participants:

                share_amount = expense_amount / len(participants)

                expense_id = add_expense(
                    trip_id,
                    expense_title,
                    expense_amount,
                    expense_paid_by,
                    expense_date,
                   
                )

                for member in participants:

                    add_expense_participant(
                        expense_id,
                        member["id"],
                        share_amount
                    )

        return redirect(f"/manage-expenses/{trip_id}")

    trip = get_trip(trip_id)
    members = get_members(trip_id)
    expenses = get_expenses(trip_id)
    trips = get_trips()

    return render_template(
        "manage_expenses.html",
        trip=trip,
        members=members,
        expenses=expenses,
        trips=trips
    )

if __name__ == "__main__":
    app.run(debug=True)