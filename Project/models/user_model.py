from flask_mysqldb import MySQL
import hashlib

mysql = None

def init_db(app):
    global mysql
    mysql = MySQL(app)

def create_user(name, nid, email, password):
    cursor = mysql.connection.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute(
        """
        INSERT INTO users (name, nid, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (name, nid, email, password_hash)
    )

    mysql.connection.commit()
    cursor.close()
def create_booking(user_id, ticket_type, source, destination, departure_date, return_date, passengers, travel_class):
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        INSERT INTO bookings 
        (user_id, ticket_type, source, destination, departure_date, return_date, passengers, class) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, ticket_type, source, destination, departure_date, return_date, passengers, travel_class)
    )
    mysql.connection.commit()
    cursor.close()

def get_user_by_email_password(email, password):
    cursor = mysql.connection.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id, name, nid, email FROM users WHERE email=%s AND password=%s",
        (email, password_hash)
    )
    user = cursor.fetchone()
    cursor.close()
    return user

def get_user_by_id(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT id, name, nid, email FROM users WHERE id=%s",
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()
    return user

def update_user(user_id, name, nid, email, new_password=None):
    cursor = mysql.connection.cursor()
    if new_password:
        import hashlib
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute(
            """
            UPDATE users
            SET name=%s, nid=%s, email=%s, password=%s
            WHERE id=%s
            """,
            (name, nid, email, password_hash, user_id)
        )
    else:
        cursor.execute(
            """
            UPDATE users
            SET name=%s, nid=%s, email=%s
            WHERE id=%s
            """,
            (name, nid, email, user_id)
        )
    mysql.connection.commit()
    cursor.close()

def delete_user(user_id):
    cursor = mysql.connection.cursor()
    
    cursor.execute("DELETE FROM bookings WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM feedbacks WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    mysql.connection.commit()
    cursor.close()


def get_user_bookings(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, user_id, ticket_type, source, destination, departure_date, 
               return_date, passengers, class, created_at
        FROM bookings 
        WHERE user_id = %s 
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    bookings = cursor.fetchall()
    cursor.close()
    return bookings


def get_booking_by_id(booking_id, user_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, ticket_type, source, destination, departure_date, 
               return_date, passengers, class, created_at
        FROM bookings 
        WHERE id = %s AND user_id = %s
        """,
        (booking_id, user_id)
    )
    booking = cursor.fetchone()
    cursor.close()
    return booking

def update_booking_status(booking_id, user_id, status):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE bookings SET status = %s WHERE id = %s AND user_id = %s",
        (status, booking_id, user_id)
    )
    mysql.connection.commit()
    cursor.close()

def delete_booking(booking_id, user_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "DELETE FROM bookings WHERE id = %s AND user_id = %s",
        (booking_id, user_id)
    )
    mysql.connection.commit()
    cursor.close()

def get_all_schedules():
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, train_number, train_name, start_station, end_station, 
               departure_time, arrival_time, frequency, status, route_description, created_at
        FROM schedules 
        ORDER BY created_at DESC
        """
    )
    schedules = cursor.fetchall()
    cursor.close()
    return schedules


def generate_tracking_id():
    """Generate a unique tracking ID"""
    year = datetime.now().year
    random_part = ''.join(random.choices(string.digits, k=3))
    return f"LF{year}{random_part}"

def create_lost_item_report(user_id, item_name, category, location, date_lost, description, contact):
    """Create a new lost item report"""
    cursor = mysql.connection.cursor()
    

    tracking_id = generate_tracking_id()
    

    while True:
        cursor.execute("SELECT id FROM lost_items WHERE tracking_id = %s", (tracking_id,))
        if not cursor.fetchone():
            break
        tracking_id = generate_tracking_id()
    
    cursor.execute(
        """
        INSERT INTO lost_items 
        (user_id, item_name, category, location, date_lost, description, contact_info, tracking_id, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """,
        (user_id, item_name, category, location, date_lost, description, contact, tracking_id)
    )
    mysql.connection.commit()
    cursor.close()
    
    return tracking_id

def get_lost_item_by_tracking_id(tracking_id):
    """Get lost item details by tracking ID"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, user_id, item_name, category, location, date_lost, 
               description, contact_info, status, tracking_id, created_at
        FROM lost_items 
        WHERE tracking_id = %s
        """,
        (tracking_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return {
            'id': result[0],
            'user_id': result[1],
            'item_name': result[2],
            'category': result[3],
            'location': result[4],
            'date_lost': result[5],
            'description': result[6],
            'contact_info': result[7],
            'status': result[8],
            'tracking_id': result[9],
            'created_at': result[10]
        }
    return None

def get_user_lost_items(user_id):
    """Get all lost items reported by a user"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, item_name, category, location, date_lost, 
               description, contact_info, status, tracking_id, created_at
        FROM lost_items 
        WHERE user_id = %s 
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    items = cursor.fetchall()
    cursor.close()
    return items

def update_lost_item_status(item_id, new_status):
    """Update the status of a lost item"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE lost_items SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (new_status, item_id)
    )
    mysql.connection.commit()
    cursor.close()


def get_user_upcoming_trips(user_id):
    """Get upcoming trips for a user"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, ticket_type, source, destination, departure_date,
               return_date, passengers, class, created_at
        FROM bookings
        WHERE user_id = %s AND departure_date >= CURDATE()
        ORDER BY departure_date ASC
        LIMIT 5
        """,
        (user_id,)
    )
    trips = cursor.fetchall()
    cursor.close()
    return trips

def get_user_recent_activity(user_id):
    """Get recent booking activity for a user"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, ticket_type, source, destination, departure_date, created_at
        FROM bookings
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,)
    )
    activities = cursor.fetchall()
    cursor.close()
    return activities

def create_notification(user_id, title, message, notification_type='info'):
    """Create a notification for a user"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
        VALUES (%s, %s, %s, %s, 0, NOW())
        """,
        (user_id, title, message, notification_type)
    )
    mysql.connection.commit()
    cursor.close()

def get_user_notifications(user_id, limit=5):
    """Get notifications for a user"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        """
        SELECT id, title, message, type, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (user_id, limit)
    )
    notifications = cursor.fetchall()
    cursor.close()
    return notifications

def mark_notification_as_read(notification_id, user_id):
    """Mark a notification as read"""
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s",
        (notification_id, user_id)
    )
    mysql.connection.commit()
    cursor.close()

def get_admin_by_credentials(admin_id, password):
    cursor = mysql.connection.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id FROM admins WHERE id=%s AND password=%s",
        (admin_id, password_hash)
    )
    admin = cursor.fetchone()
    cursor.close()
    return admin

def create_admin(admin_id, password):
    cursor = mysql.connection.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO admins (id, password) VALUES (%s, %s)",
        (admin_id, password_hash)
    )
    mysql.connection.commit()
    cursor.close()










































































