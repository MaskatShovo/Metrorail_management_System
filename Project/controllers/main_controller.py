from flask import Blueprint, render_template, request, redirect, url_for, flash , jsonify,session
from models.user_model import create_user, get_user_by_email_password, get_user_by_id, update_user, delete_user
    

main_routes = Blueprint("main_routes", __name__)

@main_routes.route("/")
def home():
    return render_template("front.html")

@main_routes.route("/auth")
def auth():
    return render_template("authentication.html")


@main_routes.route("/create-account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            nid = request.form["national-id"].strip()
            email = request.form["email"].strip()
            password = request.form["password"].strip()
            confirm = request.form["confirm-password"].strip()

            if password != confirm:
                flash("Passwords do not match!", "error")
                return redirect(url_for("main_routes.create_account"))

            create_user(name, nid, email, password)
            flash("Account created successfully!", "success")
            return redirect(url_for("main_routes.userpage"))
        except Exception as exc:
            flash(f"Error: {exc}", "error")
    return render_template("create-account.html")


@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json(silent=True) or {}
            email = (data.get("email") or "").strip()
            password = (data.get("password") or "").strip()
        else:
            email = (request.form.get("email") or "").strip()
            password = (request.form.get("password") or "").strip()

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("main_routes.login"))

        user = get_user_by_email_password(email, password)
        if user:
            
            session["user"] = {
                "id": user[0],
                "name": user[1],
                "nid": user[2],
                "email": user[3],
            }
            flash("Login successful!", "success")
            return redirect(url_for("main_routes.userpage"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("main_routes.login"))

    return render_template("login.html")



@main_routes.route("/userpage")
def userpage():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))

    db_user = get_user_by_id(session["user"]["id"])
    if not db_user:
        session.clear()
        flash("Account no longer exists.", "error")
        return redirect(url_for("main_routes.home"))

 
    user = {
        "id": db_user[0],
        "name": db_user[1],
        "nid": db_user[2],
        "email": db_user[3],
    }


    announcements = []
    return render_template("userpage.html", user=user, announcements=announcements)


@main_routes.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main_routes.login"))


@main_routes.route("/user/update", methods=["GET", "POST"])
def update_profile():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))

    user_id = session["user"]["id"]

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        nid = (request.form.get("nid") or "").strip()
        email = (request.form.get("email") or "").strip()
        new_password = (request.form.get("password") or "").strip()
        confirm = (request.form.get("confirm_password") or "").strip()

        if not name or not nid or not email:
            flash("Name, NID, and Email are required.", "error")
            return redirect(url_for("main_routes.update_profile"))

        if new_password or confirm:
            if new_password != confirm:
                flash("Passwords do not match.", "error")
                return redirect(url_for("main_routes.update_profile"))
            update_user(user_id, name, nid, email, new_password)
        else:
            update_user(user_id, name, nid, email, None)

   
        session["user"]["name"] = name
        session["user"]["nid"] = nid
        session["user"]["email"] = email

        flash("Profile updated successfully.", "success")
        return redirect(url_for("main_routes.userpage"))

   
    db_user = get_user_by_id(user_id)
    if not db_user:
        session.clear()
        flash("Account no longer exists.", "error")
        return redirect(url_for("main_routes.home"))

    user = {"id": db_user, "name": db_user[1], "nid": db_user[2], "email": db_user[3]}
    return render_template("update.html", user=user)

@main_routes.route("/user/delete", methods=["POST"])
def delete_profile():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))

    user_id = session["user"]["id"]
    try:
        delete_user(user_id)
        session.clear()
        flash("Your profile has been deleted.", "info")
        return redirect(url_for("main_routes.home"))
    except Exception as e:
        flash(f"Failed to delete profile: {e}", "error")
        return redirect(url_for("main_routes.userpage"))

@main_routes.route("/fare_calculator")
def fare_calculator():
    return render_template("fare_calculator.html")

@main_routes.route("/train_schedule")
def train_schedule():
    return render_template("train_schedule.html")

@main_routes.route("/ticket_history")
def ticket_history():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))

    user_id = session["user"]["id"]
    bookings = get_user_bookings(user_id)

    processed_bookings = []
    for booking in bookings:
        from datetime import datetime, date


        if isinstance(booking[5], str):
            departure_date = datetime.strptime(booking[5], '%Y-%m-%d').date()
        else:
            departure_date = booking[5]

        status = 'upcoming' if departure_date > date.today() else 'completed'

        base_fare = {'Standard': 20, 'Premium': 30, 'First': 40}.get(booking[8], 20)
        fare = int(base_fare * 1.5 * int(booking[7]))

        processed_bookings.append({
            'id': booking[0],
            'ticket_type': booking[2],
            'source': booking[3],
            'destination': booking[4],
            'departure_date': booking[5],
            'return_date': booking[6],
            'passengers': booking[7],
            'travel_class': booking[8],
            'booking_date': booking[9],
            'status': status,
            'fare': fare
        })

    return render_template("ticket_history.html", bookings=processed_bookings)













































































# @main_routes.route("/api/book", methods=["POST"])
# def book_ticket():
#     data = request.json
#     try:
#         create_booking(
#             data["user_id"], data["route"], data["date"],
#             data["time"], data["seat_no"]
#         )
#         return jsonify({"message": "Booking successful"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @main_routes.route("/api/bookings", methods=["GET"])
# def view_bookings():
#     bookings = get_bookings()
#     return jsonify({"bookings": bookings})

# # Feature 2: Feedback
# @main_routes.route("/api/feedback", methods=["POST"])
# def give_feedback():
#     data = request.json
#     try:
#         create_feedback(data["user_id"], data["rating"], data["comment"])
#         return jsonify({"message": "Feedback submitted"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @main_routes.route("/api/feedbacks", methods=["GET"])
# def view_feedbacks():
#     feedbacks = get_feedbacks()
#     return jsonify({"feedbacks": feedbacks})
