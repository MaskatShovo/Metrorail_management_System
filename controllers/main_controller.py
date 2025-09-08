from flask import Blueprint, render_template, request, redirect, url_for, flash , jsonify,session
from models.user_model import create_user, get_user_by_email_password, get_user_by_id, update_user, delete_user, create_booking,get_user_bookings,get_booking_by_id, update_booking_status, delete_booking,create_schedule, get_all_schedules, update_schedule1, delete_schedule,get_admin_by_credentials, create_lost_item_report, get_lost_item_by_tracking_id, get_user_recent_activity, get_user_upcoming_trips, get_user_notifications,mark_notification_as_read,get_total_bookings_count,create_feedback, get_user_feedbacks, get_monthly_revenue,create_announcement, get_all_announcements, delete_announcement,get_user_total_points, redeem_points ,get_user_favorite_destinations, add_favorite_destination, remove_favorite_destination,update_user_language, get_user_language
# from Project import mysql


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
import io
from datetime import datetime
from flask import send_file


main_routes = Blueprint("main_routes", __name__)

# @main_routes.route("/")
# def home():
#     return render_template("front.html")

@main_routes.route("/")
def home():
    announcements = get_all_announcements()
    return render_template("front.html", announcements=announcements)

@main_routes.route("/auth")
def auth():
    return render_template("authentication.html")

@main_routes.route("/fare_calculator")
def fare_calculator():
    return render_template("fare_calculator.html")

@main_routes.route("/train_schedule")
def train_schedule():
    try:
        schedules = get_all_schedules()
        current_time = datetime.now().strftime('%H:%M')
        return render_template("train_schedule.html", 
                             schedules=schedules, 
                             getStationName=get_station_name,
                             current_time=current_time)
    except Exception as e:
        print(f"Error fetching schedules: {e}")
        current_time = datetime.now().strftime('%H:%M')
        return render_template("train_schedule.html", 
                             schedules=[], 
                             getStationName=get_station_name,
                             current_time=current_time)


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
            return redirect(url_for("main_routes.login"))
        except Exception as exc:
            flash(f"Error: {exc}", "error")
    return render_template("create-account.html")


@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Clear any existing flash messages at the start of login
        session.pop('_flashes', None)
        
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

@main_routes.route("/w2", methods=["GET", "POST"])
def w2():
    return render_template("w2.html")

@main_routes.route("/w3", methods=["GET", "POST"])
def w3():
    return render_template("w3.html")

@main_routes.route("/w4", methods=["GET", "POST"])
def w4():
    return render_template("w4.html")



@main_routes.route("/logout")
def logout():
    was_logged_in = "user" in session
    session.clear()
    
    if was_logged_in:
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




@main_routes.route("/book_tickets", methods=["GET", "POST"])
def book_tickets():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))

    if request.method == "POST":
        try:
            user_id = session["user"]["id"]
            ticket_type = request.form.get("ticketType")
            source = request.form.get("source")
            destination = request.form.get("destination")
            departure_date = request.form.get("departureDate")
            return_date = request.form.get("returnDate") or None
            passengers = request.form.get("passengers")
            travel_class = request.form.get("class")

            if not all([ticket_type, source, destination, departure_date, passengers, travel_class]):
                flash("Please fill in all required fields.", "error")
                return redirect(url_for("main_routes.book_tickets"))

            if source == destination:
                flash("Source and destination cannot be the same!", "error")
                return redirect(url_for("main_routes.book_tickets"))

            if ticket_type == "return" and not return_date:
                flash("Return date is required for return tickets.", "error")
                return redirect(url_for("main_routes.book_tickets"))

            # Calculate fare
            base_fare = {'Standard': 20, 'Premium': 30, 'First': 40}.get(travel_class, 20)
            fare = int(base_fare * 1.5 * int(passengers))
            points = 10

            # Create booking with fare
            create_booking(user_id, ticket_type, source, destination, departure_date, return_date, passengers, travel_class, fare)

            flash("🎉 Ticket booked successfully! You earned 10 points!", "success")

            return redirect(url_for("main_routes.userpage"))

        except Exception as e:
            flash(f"Failed to book ticket: {str(e)}", "error")
            return redirect(url_for("main_routes.book_tickets"))

    return render_template("book_tickets.html")





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





def generate_qr_code(data):
    """Generate QR code and return as image buffer"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
   
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_ticket_receipt_pdf(booking_data, user_data):
    """Create a bus ticket style PDF receipt"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=0.5*inch, leftMargin=0.5*inch,
                          topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#059669'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#047857'),
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
 
    story.append(Paragraph("🚊 DHAKA METRO RAIL", title_style))
    story.append(Paragraph("OFFICIAL TICKET RECEIPT", header_style))
    story.append(Spacer(1, 20))
    
    # Ticket Information Table
    ticket_data = [
        ['TICKET DETAILS', ''],
        ['Ticket ID:', f"MR{booking_data['id']}"],
        ['Passenger Name:', user_data['name']],
        ['National ID:', user_data['nid']],
        ['Email:', user_data['email']],
        ['', ''],
        ['JOURNEY INFORMATION', ''],
        ['From Station:', booking_data['source']],
        ['To Station:', booking_data['destination']],
        ['Departure Date:', booking_data['departure_date'].strftime('%B %d, %Y') if booking_data['departure_date'] else 'N/A'],
        ['Return Date:', booking_data['return_date'].strftime('%B %d, %Y') if booking_data.get('return_date') else 'One Way'],
        ['Ticket Type:', booking_data['ticket_type'].title()],
        ['Travel Class:', booking_data['travel_class']],
        ['Passengers:', str(booking_data['passengers'])],
        ['', ''],
        ['PAYMENT INFORMATION', ''],
        ['Fare Amount:', f"৳{booking_data['fare']}"],
        ['Status:', booking_data['status'].title()],
        ['Booking Date:', booking_data['booking_date'].strftime('%B %d, %Y at %I:%M %p')],
    ]
    
    # Create table
    table = Table(ticket_data, colWidths=[2.5*inch, 3*inch])
    table.setStyle(TableStyle([
        # Header rows styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#059669')),
        ('BACKGROUND', (0, 15), (-1, 15), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 6), (-1, 6), colors.whitesmoke),
        ('TEXTCOLOR', (0, 15), (-1, 15), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ('FONTNAME', (0, 15), (-1, 15), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 6), (-1, 6), 12),
        ('FONTSIZE', (0, 15), (-1, 15), 12),
        
        # Data styling
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Generate QR Code
    qr_data = f"MR{booking_data['id']}|{user_data['name']}|{booking_data['source']}|{booking_data['destination']}|{booking_data['fare']}"
    qr_buffer = generate_qr_code(qr_data)
    
    # Create QR code section
    qr_style = ParagraphStyle(
        'QRStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("Scan QR Code for Verification", qr_style))
    
    # Add QR code image
    qr_img = Image(qr_buffer, width=1.5*inch, height=1.5*inch)
    qr_img.hAlign = 'CENTER'
    story.append(qr_img)
    story.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey,
        fontName='Helvetica'
    )
    
    footer_text = f"""
    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
    This is a computer-generated receipt. No signature required.<br/>
    For support, contact: support@dhakaMetrorail.gov.bd | +880-2-XXXXXXXX<br/>
    Thank you for choosing Dhaka Metro Rail!
    """
    
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# Add this route to your main_controller.py
@main_routes.route("/download_receipt/<int:booking_id>")
def download_receipt(booking_id):
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))
    
    user_id = session["user"]["id"]
    
    # Get booking data
    booking = get_booking_by_id(booking_id, user_id)
    
    if not booking:
        flash("Ticket not found", "error")
        return redirect(url_for("main_routes.ticket_history"))
    
    # Get user data
    user_data = session["user"]
    
    # Process booking data
    from datetime import datetime, date
    
    departure_date = booking[4]
    if isinstance(departure_date, str):
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
    
    return_date = booking[5]
    if return_date and isinstance(return_date, str):
        return_date = datetime.strptime(return_date, '%Y-%m-%d').date()
    
    status = 'upcoming' if departure_date > date.today() else 'completed'
    
    # Calculate fare
    base_fare = {'Standard': 20, 'Premium': 30, 'First': 40}.get(booking[7], 20)
    fare = int(base_fare * 1.5 * int(booking[6]))
    
    booking_data = {
        'id': booking[0],
        'ticket_type': booking[1],
        'source': booking[2],
        'destination': booking[3],
        'departure_date': departure_date,
        'return_date': return_date,
        'passengers': booking[6],
        'travel_class': booking[7],
        'booking_date': booking[8],
        'status': status,
        'fare': fare
    }
    
    # Generate PDF
    pdf_buffer = create_ticket_receipt_pdf(booking_data, user_data)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'MetroRail_Receipt_MR{booking_id}.pdf',
        mimetype='application/pdf'
    )


@main_routes.route("/cancel_refund")
def cancel_refund():
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
        
        # Check if booking has status column, if not assign based on date
        status = getattr(booking, 'status', None) or ('upcoming' if departure_date > date.today() else 'completed')
        
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
    
    return render_template("cancel_refund.html", bookings=processed_bookings)

@main_routes.route("/cancel_ticket/<int:booking_id>", methods=["POST"])
def cancel_ticket(booking_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    
    try:
        update_booking_status(booking_id, user_id, 'cancelled')
        return jsonify({"success": True, "message": "Ticket cancelled successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_routes.route("/process_refund/<int:booking_id>", methods=["POST"])
def process_refund(booking_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    
    try:
        update_booking_status(booking_id, user_id, 'refunded')
        return jsonify({"success": True, "message": "Refund processed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main_routes.route("/admin_schedules")
def admin_schedules():
    schedules = get_all_schedules()
    return render_template("admin_e.html", schedules=schedules, getStationName=get_station_name)

@main_routes.route("/add_schedule", methods=["POST"])
def add_schedule():
    try:
        train_number = request.form.get("trainNumber")
        train_name = request.form.get("trainName")
        start_station = request.form.get("startStation")
        end_station = request.form.get("endStation")
        departure_time = request.form.get("departureTime")
        arrival_time = request.form.get("arrivalTime")
        frequency = request.form.get("frequency")
        status = request.form.get("status")
        route_description = request.form.get("route")

        create_schedule(train_number, train_name, start_station, end_station, 
                      departure_time, arrival_time, frequency, status, route_description)
        
        return jsonify({"success": True, "message": "Schedule added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_routes.route("/delete_schedule/<int:schedule_id>", methods=["DELETE"])
def delete_schedule_route(schedule_id):
    try:
        delete_schedule(schedule_id)
        return jsonify({"success": True, "message": "Schedule deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from models.user_model import get_admin_by_credentials

@main_routes.route("/update_schedule", methods=["POST"])
def update_schedule_route():
    try:
        schedule_id = request.form.get("scheduleId")
        train_number = request.form.get("trainNumber")
        train_name = request.form.get("trainName")
        start_station = request.form.get("startStation")
        end_station = request.form.get("endStation")
        departure_time = request.form.get("departureTime")
        arrival_time = request.form.get("arrivalTime")
        frequency = request.form.get("frequency")
        status = request.form.get("status")
        route_description = request.form.get("route")

        update_schedule1(schedule_id, train_number, train_name, start_station, end_station, 
                       departure_time, arrival_time, frequency, status, route_description)
        
        return jsonify({"success": True, "message": "Schedule updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_routes.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id", "").strip()
        password = request.form.get("password", "").strip()

        if not admin_id or not password:
            flash("Admin ID and password are required.", "error")
            return redirect(url_for("main_routes.admin_login"))

        admin = get_admin_by_credentials(admin_id, password)
        if admin:
            session["admin"] = {"id": admin[0]}  # Change this line
            flash("Admin login successful!", "success")
            return redirect(url_for("main_routes.admin_dashboard"))
        else:
            flash("Invalid admin credentials", "error")
            return redirect(url_for("main_routes.admin_login"))

    return render_template("admin_login.html")

@main_routes.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        flash("Please log in as admin first", "error")
        return redirect(url_for("main_routes.admin_login"))
    
    # Get total bookings count and monthly revenue
    total_bookings = get_total_bookings_count()
    monthly_revenue = get_monthly_revenue()
    
    return render_template("admin_dashboard.html", 
                         total_bookings=total_bookings, 
                         monthly_revenue=monthly_revenue)

    
    return render_template("admin_dashboard.html", total_bookings=total_bookings)
@main_routes.route("/admin_logout")
def admin_logout():
    if "admin" in session:
        session.pop("admin")
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("main_routes.admin_login"))


def get_station_name(value):
    station_names = {
        "uttara-north": "Uttara North",
        "uttara-center": "Uttara Center",
        "uttara-south": "Uttara South",
        "pallabi": "Pallabi",
        "mirpur-11": "Mirpur 11",
        "mirpur-10": "Mirpur 10",
        "kazipara": "Kazipara",
        "shewrapara": "Shewrapara",
        "agargaon": "Agargaon",
        "bijoy-sarani": "Bijoy Sarani",
        "farmgate": "Farmgate",
        "karwan-bazar": "Karwan Bazar",
        "shahbagh": "Shahbagh",
        "dhaka-university": "Dhaka University",
        "bangladesh-secretariat": "Bangladesh Secretariat",
        "motijheel": "Motijheel",
    }
    return station_names.get(value, value)

@main_routes.route("/test", methods=["GET", "POST"])
def test():
    return render_template("test.html")

@main_routes.route("/lost_found")
def lost_found():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))
    
    return render_template("lost_found.html")

@main_routes.route("/report_lost_item", methods=["POST"])
def report_lost_item():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))
    
    try:
        user_id = session["user"]["id"]
        item_name = request.form.get("itemName").strip()
        category = request.form.get("category").strip()
        location = request.form.get("location").strip()
        date_lost = request.form.get("date")
        description = request.form.get("description", "").strip()
        contact = request.form.get("contact").strip()
        
        if not all([item_name, category, location, date_lost, contact]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("main_routes.lost_found"))
        
        tracking_id = create_lost_item_report(user_id, item_name, category, location, date_lost, description, contact)
        flash(f"Item reported successfully! Your tracking ID is: {tracking_id}. Please save this ID to track your item status.", "success")
        return redirect(url_for("main_routes.lost_found"))
        
    except Exception as e:
        flash(f"Failed to report item: {str(e)}", "error")
        return redirect(url_for("main_routes.lost_found"))

@main_routes.route("/track_lost_item", methods=["POST"])
def track_lost_item():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))
    
    tracking_id = request.form.get("trackingId", "").strip().upper()
    
    if not tracking_id:
        flash("Please enter a tracking ID", "error")
        return redirect(url_for("main_routes.lost_found"))
    
    tracking_result = get_lost_item_by_tracking_id(tracking_id)
    
    if not tracking_result:
        flash("Tracking ID not found. Please check your ID and try again.", "error")
        return render_template("lost_found.html", tracking_result=None)
    
    return render_template("lost_found.html", tracking_result=tracking_result)



@main_routes.route("/userpage")
def userpage():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))

    user_id = session["user"]["id"]
    db_user = get_user_by_id(user_id)
    
    if not db_user:
        session.clear()
        flash("Account no longer exists.", "error")
        return redirect(url_for("main_routes.home"))
    #user_language = get_user_language(user_id)
    user = {
        "id": db_user[0],
        "name": db_user[1],
        "nid": db_user[2],
        "email": db_user[3],
        #"language": user_language
    }

    # Get dashboard data
    upcoming_trips = get_user_upcoming_trips(user_id)
    recent_activity = get_user_recent_activity(user_id)
    notifications = get_user_notifications(user_id)
    favorite_destinations = get_user_favorite_destinations(user_id)
    
    # Process upcoming trips data
    processed_trips = []
    for trip in upcoming_trips:
        from datetime import datetime, date
        departure_date = trip[4]
        if isinstance(departure_date, str):
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
        
        # Calculate days until trip
        days_until = (departure_date - date.today()).days
        
        processed_trips.append({
            'id': trip[0],
            'ticket_type': trip[1],
            'source': trip[2],
            'destination': trip[3],
            'departure_date': departure_date,
            'return_date': trip[5],
            'passengers': trip[6],
            'travel_class': trip[7],
            'days_until': days_until
        })

    # Process recent activity
    processed_activity = []
    for activity in recent_activity:
        processed_activity.append({
            'id': activity[0],
            'ticket_type': activity[1],
            'source': activity[2],
            'destination': activity[3],
            'departure_date': activity[4],
            'booking_date': activity[5]
        })
    stations = [
        {"code": "uttara-north", "name": "Uttara North"},
        {"code": "uttara-center", "name": "Uttara Center"},
        {"code": "uttara-south", "name": "Uttara South"},
        {"code": "pallabi", "name": "Pallabi"},
        {"code": "mirpur-11", "name": "Mirpur 11"},
        {"code": "mirpur-10", "name": "Mirpur 10"},
        {"code": "kazipara", "name": "Kazipara"},
        {"code": "shewrapara", "name": "Shewrapara"},
        {"code": "agargaon", "name": "Agargaon"},
        {"code": "bijoy-sarani", "name": "Bijoy Sarani"},
        {"code": "farmgate", "name": "Farmgate"},
        {"code": "karwan-bazar", "name": "Karwan Bazar"},
        {"code": "shahbagh", "name": "Shahbagh"},
        {"code": "dhaka-university", "name": "Dhaka University"},
        {"code": "bangladesh-secretariat", "name": "Bangladesh Secretariat"},
        {"code": "motijheel", "name": "Motijheel"}
    ]
    return render_template("userpage.html", 
                         user=user, 
                         upcoming_trips=processed_trips,
                         recent_activity=processed_activity,
                         notifications=notifications,
                         favorite_destinations=favorite_destinations,
                         stations=stations)

# Add route to mark notifications as read
@main_routes.route("/mark_notification_read/<int:notification_id>", methods=["POST"])
def mark_notification_read(notification_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    try:
        mark_notification_as_read(notification_id, user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@main_routes.route("/time_calculator")
def time_calculator():
    return render_template("time_calculator.html")


@main_routes.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))
    
    if request.method == "POST":
        try:
            user_id = session["user"]["id"]
            rating = request.form.get("rating")
            category = request.form.get("category")
            subject = request.form.get("subject").strip()
            message = request.form.get("message").strip()
            
            if not all([rating, category, subject, message]):
                flash("Please fill in all required fields.", "error")
                return redirect(url_for("main_routes.feedback"))
            
            if not (1 <= int(rating) <= 5):
                flash("Please select a valid rating between 1 and 5.", "error")
                return redirect(url_for("main_routes.feedback"))
            
            create_feedback(user_id, int(rating), category, subject, message)
            flash("Thank you for your feedback! We appreciate your input.", "success")
            return redirect(url_for("main_routes.userpage"))
            
        except Exception as e:
            flash(f"Failed to submit feedback: {str(e)}", "error")
            return redirect(url_for("main_routes.feedback"))
    
    return render_template("feedback.html")



@main_routes.route("/welcome_tour")
def welcome_tour():
    return render_template("welcome_tour.html")



@main_routes.route("/announcements")
def announcements():
    if "admin" not in session:
        flash("Please log in as admin first", "error")
        return redirect(url_for("main_routes.admin_login"))
    
    announcements = get_all_announcements()
    return render_template("announcement.html", announcements=announcements)

@main_routes.route("/add_announcement", methods=["POST"])
def add_announcement():
    if "admin" not in session:
        return jsonify({"error": "Admin access required"}), 401
    
    try:
        announcement_type = request.form.get("type", "").strip()
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        
        print(f"Received data: type={announcement_type}, title={title}, message={message}")  # Debug line
        
        if not announcement_type or not title or not message:
            return jsonify({"error": "All fields are required"}), 400
            
        create_announcement(announcement_type, title, message)
        return jsonify({"success": True, "message": "Announcement added successfully!"})
    except Exception as e:
        print(f"Error in add_announcement: {e}")  # Debug line
        return jsonify({"error": str(e)}), 500

@main_routes.route("/delete_announcement/<int:announcement_id>", methods=["DELETE"])
def delete_announcement_route(announcement_id):
    if "admin" not in session:
        return jsonify({"error": "Admin access required"}), 401
    
    try:
        delete_announcement(announcement_id)
        return jsonify({"success": True, "message": "Announcement deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_routes.route("/announcements_data")
def announcements_data():
    if "admin" not in session:
        return jsonify({"error": "Admin access required"}), 401
    
    announcements = get_all_announcements()
    announcements_list = []
    
    for announcement in announcements:
        announcements_list.append({
            'id': announcement[0],
            'type': announcement[1],
            'title': announcement[2],
            'message': announcement[3],
            'date': announcement[4].strftime('%m/%d/%Y') if announcement[4] else ''
        })
    
    return jsonify(announcements_list)




# New route for reward points page
@main_routes.route("/reward_points")
def reward_points():
    if "user" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("main_routes.login"))
    
    user_id = session["user"]["id"]
    total_points = get_user_total_points(user_id)
    
    return render_template("reward_points.html", total_points=total_points)

# New endpoint for processing redemption (called via JS)
@main_routes.route("/redeem_points", methods=["POST"])
def redeem_points_route():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    total_points = get_user_total_points(user_id)
    
    if total_points < 500:
        return jsonify({"error": "Insufficient points"}), 400
    
    try:
        redeem_points(user_id, 500)  # Deduct 500 points for ৳100
        return jsonify({"success": True, "message": "Redemption successful! ৳100 credited via selected method."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main_routes.route("/add_favorite", methods=["POST"])
def add_favorite():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    destination_name = request.form.get("destinationName", "").strip()
    station_code = request.form.get("stationCode", "").strip()
    
    if not destination_name or not station_code:
        return jsonify({"error": "Destination name and station code are required"}), 400
    
    try:
        add_favorite_destination(user_id, destination_name, station_code)
        return jsonify({"success": True, "message": "Favorite destination added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_routes.route("/remove_favorite/<int:favorite_id>", methods=["DELETE"])
def remove_favorite(favorite_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    
    try:
        remove_favorite_destination(user_id, favorite_id)
        return jsonify({"success": True, "message": "Favorite destination removed successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route("/update_language", methods=["POST"])
def update_language():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session["user"]["id"]
    language = request.form.get("language", "").strip()
    
    if not language or language not in ['en', 'bn']:  # English and Bengali
        return jsonify({"error": "Invalid language selection"}), 400
    
    try:
        update_user_language(user_id, language)
        session["user"]["language"] = language  # Update session
        return jsonify({"success": True, "message": "Language updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


























