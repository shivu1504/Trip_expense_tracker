from decimal import Decimal, ROUND_DOWN
from flask import Flask, render_template, request, redirect

from database import (
    get_trips,
    get_members,
    get_member,
    add_trip,
    get_trip,
    get_trip_by_code,
    join_trip,
    add_member,
    get_expenses,
    add_expense,
    add_expense_participant,
    get_split_totals,
    get_total_paid,
    get_balances,
    update_trip,
    delete_trip,
    update_member,
    get_expense,
    get_expense_participants,
    update_expense,
    delete_expense,
    initialize_database
)


app = Flask(__name__)


def calculate_participant_shares(amount, participants):
    amount = Decimal(str(amount)).quantize(Decimal("0.01"))
    if not participants:
        return []
    base_share = (amount / len(participants)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    remainder = int((amount - base_share * len(participants)) * 100)
    return [
        (member["id"], base_share + (Decimal("0.01") if index < remainder else Decimal("0")))
        for index, member in enumerate(participants)
    ]


def calculate_settlements(balances):
    creditors = [[item["name"], Decimal(str(item["balance"])).quantize(Decimal("0.01"))]
                 for item in balances if Decimal(str(item["balance"])) > 0]
    debtors = [[item["name"], -Decimal(str(item["balance"])).quantize(Decimal("0.01"))]
               for item in balances if Decimal(str(item["balance"])) < 0]
    settlements = []
    debtor_index = creditor_index = 0
    while debtor_index < len(debtors) and creditor_index < len(creditors):
        amount = min(debtors[debtor_index][1], creditors[creditor_index][1])
        settlements.append({"from_name": debtors[debtor_index][0],
                            "to_name": creditors[creditor_index][0], "amount": amount})
        debtors[debtor_index][1] -= amount
        creditors[creditor_index][1] -= amount
        if debtors[debtor_index][1] == 0:
            debtor_index += 1
        if creditors[creditor_index][1] == 0:
            creditor_index += 1
    return settlements


# =========================================
# DATABASE INITIALIZATION
# =========================================

initialize_database()


# =========================================
# HOME
# =========================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        trip_name = request.form["trip_name"].strip()

        member_names = request.form.getlist(
            "member_names"
        )

        member_names = [
            name.strip()
            for name in member_names
            if name.strip()
        ]

        if trip_name and member_names:

            trip_id = add_trip(trip_name)

            for member_name in member_names:

                add_member(
                    trip_id,
                    member_name
                )

            return redirect(
                f"/trip/{trip_id}"
            )

    trips = get_trips()

    return render_template(
        "index.html",
        trips=trips
    )


# =========================================
# ADD EXPENSE
# =========================================

@app.route("/add-expense")
def add_expense_page():

    trips = get_trips()

    if not trips:
        return redirect("/")

    last_trip_id = trips[0]["id"]

    return redirect(
        f"/manage-expenses/{last_trip_id}"
    )


# =========================================
# DELETE MEMBER
# =========================================

@app.route(
    "/delete-member/<int:member_id>",
    methods=["POST"]
)
def delete_member_route(member_id):

    from database import delete_member
    member = get_member(member_id)
    if member:
        delete_member(member_id)
        return redirect(f"/manage-members/{member['trip_id']}")
    return redirect("/")


@app.route("/delete-trip/<int:trip_id>", methods=["POST"])
def delete_trip_route(trip_id):
    delete_trip(trip_id)
    return redirect("/")


@app.route("/edit-trip/<int:trip_id>", methods=["GET", "POST"])
def edit_trip_route(trip_id):
    trip = get_trip(trip_id)
    if not trip:
        return redirect("/")
    if request.method == "POST":
        name = request.form.get("trip_name", "").strip()
        if name:
            update_trip(trip_id, name)
            return redirect(f"/trip/{trip_id}")
        return render_template("edit_trip.html", trip=trip, error="Trip name is required.")
    return render_template("edit_trip.html", trip=trip)


# =========================================
# TRIP PAGE
# =========================================

@app.route("/trip/<int:trip_id>")
def trip(trip_id):

    trip = get_trip(trip_id)

    if not trip:
        return redirect("/")

    members = get_members(trip_id)

    expenses = get_expenses(trip_id)

    split_totals = get_split_totals(
        trip_id
    )

    total_paid = get_total_paid(
        trip_id
    )

    balances = get_balances(trip_id)

    return render_template(
        "trip.html",
        trip=trip,
        members=members,
        expenses=expenses,
        split_totals=split_totals,
        total_paid=total_paid,
        balances=balances,
        settlements=calculate_settlements(balances)
    )


# =========================================
# TRIP MEMORY
# =========================================

@app.route("/trip-memory/<int:trip_id>")
def trip_memory(trip_id):

    trip = get_trip(trip_id)

    return render_template(
        "trip_memory.html",
        trip=trip
    )


# =========================================
# COMPLETE TRIP
# =========================================

@app.route("/complete-trip/<int:trip_id>")
def complete_trip(trip_id):

    trip = get_trip(trip_id)

    return render_template(
        "complete_trip.html",
        trip=trip
    )


# =========================================
# JOIN TRIP
# =========================================

@app.route(
    "/join-trip",
    methods=["POST"]
)
def join_trip_route():

    member_name = request.form[
        "member_name"
    ].strip()

    trip_code = request.form[
        "trip_code"
    ].strip().upper()

    if not member_name or not trip_code:

        trips = get_trips()

        return render_template(
            "index.html",
            trips=trips,
            join_error=(
                "Please enter your name "
                "and Trip Code."
            )
        )

    trip = get_trip_by_code(
        trip_code
    )

    if not trip:

        trips = get_trips()

        return render_template(
            "index.html",
            trips=trips,
            join_error=(
                "Trip Code not found. "
                "Please check the code "
                "and try again."
            )
        )

    join_trip(
        trip["id"],
        member_name
    )

    return redirect(
        f"/trip/{trip['id']}"
    )


# =========================================
# MANAGE MEMBERS
# =========================================

@app.route(
    "/manage-members/<int:trip_id>",
    methods=["GET", "POST"]
)
def manage_members(trip_id):

    trip = get_trip(trip_id)
    if not trip:
        return redirect("/")

    if request.method == "POST":

        member_name = request.form[
            "member_name"
        ].strip()

        if member_name:

            add_member(
                trip_id,
                member_name
            )

        return redirect(
            f"/manage-members/{trip_id}"
        )

    members = get_members(
        trip_id
    )

    return render_template(
        "manage_members.html",
        trip=trip,
        members=members
    )


@app.route("/edit-member/<int:member_id>", methods=["GET", "POST"])
def edit_member_route(member_id):
    member = get_member(member_id)
    if not member:
        return redirect("/")
    if request.method == "POST":
        name = request.form.get("member_name", "").strip()
        if name:
            update_member(member_id, name)
            return redirect(f"/manage-members/{member['trip_id']}")
        return render_template("edit_member.html", member=member, error="Member name is required.")
    return render_template("edit_member.html", member=member)


# =========================================
# MANAGE EXPENSES
# =========================================

@app.route("/manage-expenses/<int:trip_id>", methods=["GET", "POST"])
def manage_expenses(trip_id):
    trip = get_trip(trip_id)
    if not trip:
        return redirect("/")
    if request.method == "POST":
        title = request.form.get("expense_title", "").strip()
        try:
            amount = Decimal(request.form.get("expense_amount", "0")).quantize(Decimal("0.01"))
        except Exception:
            amount = Decimal("0")
        paid_by = request.form.get("expense_paid_by", "")
        expense_date = request.form.get("expense_date", "")
        excluded = request.form.getlist("excluded_members")
        members = get_members(trip_id)
        participants = members if request.form.get("split_type") == "all" else [
            member for member in members if str(member["id"]) not in excluded
        ]
        member_ids = {str(member["id"]) for member in members}
        if title and amount > 0 and paid_by in member_ids and expense_date and participants:
            expense_id = add_expense(trip_id, title, amount, paid_by, expense_date)
            for member_id, share_amount in calculate_participant_shares(amount, participants):
                add_expense_participant(expense_id, member_id, share_amount)
        return redirect(f"/manage-expenses/{trip_id}")
    return render_template("manage_expenses.html", trip=trip, members=get_members(trip_id),
                           expenses=get_expenses(trip_id), trips=get_trips())


@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense_route(expense_id):
    expense = get_expense(expense_id)
    if not expense:
        return redirect("/")
    trip_id = expense["trip_id"]
    members = get_members(trip_id)
    participants = get_expense_participants(expense_id)
    if request.method == "POST":
        title = request.form.get("expense_title", "").strip()
        try:
            amount = Decimal(request.form.get("expense_amount", "0")).quantize(Decimal("0.01"))
        except Exception:
            amount = Decimal("0")
        selected = members if request.form.get("split_type") == "all" else [
            member for member in members if str(member["id"]) not in request.form.getlist("excluded_members")
        ]
        member_ids = {str(member["id"]) for member in members}
        if title and amount > 0 and request.form.get("expense_paid_by") in member_ids and request.form.get("expense_date") and selected:
            update_expense(expense_id, title, amount, request.form["expense_paid_by"],
                           request.form["expense_date"], calculate_participant_shares(amount, selected))
            return redirect(f"/trip/{trip_id}")
        return render_template("edit_expense.html", expense=expense, members=members,
                               participants=participants, error="Enter valid details and select a participant.")
    return render_template("edit_expense.html", expense=expense, members=members, participants=participants)


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
def delete_expense_route(expense_id):
    expense = get_expense(expense_id)
    if not expense:
        return redirect("/")
    delete_expense(expense_id)
    return redirect(f"/trip/{expense['trip_id']}")


# =========================================
# RUN APP
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )