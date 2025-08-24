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

















































































# ///////////////////////////////////
# def create_booking(user_id, route, date, time, seat_no):
#     cursor = mysql.connection.cursor()
#     cursor.execute(
#         """INSERT INTO bookings (user_id, route, date, time, seat_no)
#            VALUES (%s, %s, %s, %s, %s)""",
#         (user_id, route, date, time, seat_no)
#     )
#     mysql.connection.commit()
#     cursor.close()

# def get_bookings():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM bookings")
#     rows = cursor.fetchall()
#     cursor.close()

    
#     bookings = []
#     for row in rows:
#         bookings.append({
#             "id": row[0],
#             "user_id": row[1],
#             "route": row[2],
#             "date": str(row[3]),      
#             "time": str(row[4]),      
#             "seat_no": row[5],
#             "created_at": str(row[6])  
#         })
#     return bookings
