from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from datetime import datetime, timedelta, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract, and_
import threading
from flask_mail import Mail, Message
import pandas as pd
import os
from werkzeug.utils import secure_filename
import requests
from twilio.rest import Client
import schedule
import time

is_rashberrypi = False
# is_rashberrypi = True

debug_mode = not is_rashberrypi

edit_password = "00000"
# Login credentials
USERNAME = "admin"
PASSWORD = "admin"

daily_mail_email_id = "lotusaquafarms@yahoo.com"
daily_report_schedule_time = "19:00"  # 24-hour format (HH:MM)

email_id = "lotusaquaiotprojects@gmail.com"
email_password = "zxxr noif fdcq qnro"

esp32_ip = "192.168.1.100"  # Change to your ESP32 IP
esp32_api = "esp_update_token"
# token_id_reset_value = 50

# Twilio credentials from your account
account_sid = 'AC47072dc2d5361ca5cab0e1a4f7efd369gokul'  #remove the gokul postfix
auth_token = '5ee9d4d01b69688e77bc548fcfbf79c1'
msg_gopi_send_number = "+919791898999"
schedule_time_1 = "17:45"  # 24-hour format (HH:MM)
schedule_time_2 = "18:30"  # 24-hour format (HH:MM)

twilio_whatsapp_number = '+15557390616'  # Provided by Twilio
twilio_number = "+12317902355"

is_sms_required = False

default_item_id = 1 # water Bottol
gst_rate = 0.12        

# below for testing
# account_sid = 'AC47072dc2d5361ca5cab0e1a4f7efd369fgokul'  #remove the gokul postfix
# auth_token = '5ee9d4d01b69688e77bc548fcfbf79c1'
# msg_send_number = "8220339908"
# schedule_time_1 = "18:53"  # 24-hour format (HH:MM)
# schedule_time_2 = "18:54"  # 24-hour format (HH:MM)

client = Client(account_sid, auth_token)

#blynk app
# Your Blynk credentials

BLYNK_TEMPLATE_ID = "TMPL30bfSmreb"
BLYNK_TEMPLATE_NAME = "Water Can Management"
BLYNK_AUTH_TOKEN = "UR19Oqzy9tEpBMJkyglVvSxPBBJppNoR"

VIRTUAL_PIN = 'V0'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
app.secret_key = 'ticket-management'  # Add this line
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dealers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=24)
db = SQLAlchemy(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update based on your email provider
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = email_id  # Update with your email
app.config['MAIL_PASSWORD'] = email_password  # Use an app password if required

mail = Mail(app)

# Database model for dealer data
class Dealer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.String(100), nullable=False)
    water_can_count = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    token_id = db.Column(db.Integer, nullable=False)  # Daily resetting token ID
    #date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)  # Store the date of entry

    def __repr__(self):
        return f'<Dealer {self.dealer_id}>'
    
    @property
    def formatted_date(self):
        return self.timestamp.strftime("%d-%m-%Y")  # Format the date

    @property
    def formatted_time(self):
        return self.timestamp.strftime("%I:%M %p")  # Format the time in 12-hour format

#Dealer details
class Dealer_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(400), nullable=True)
    aadhaar_file = db.Column(db.String(400))  # Path to Aadhaar copy
    photo_file = db.Column(db.String(400)) 

class DealerAccounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.String(100), db.ForeignKey('dealer_details.dealer_id'), nullable=False, unique=True)
    current_balance = db.Column(db.Float, default=0.0)
    last_payment_date = db.Column(db.DateTime)

    dealer = db.relationship('Dealer_details', backref='account')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    shop_name = db.Column(db.String(100), nullable=False)
    total = db.Column(db.String(100), nullable=False)
    amount_paid = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)

class BillingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    billing_id = db.Column(db.Integer, nullable=False)
    dealer_id = db.Column(db.String(100), db.ForeignKey('dealer_details.dealer_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer, nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, nullable=False)
    grand_total = db.Column(db.Float, nullable=False)
    credit_balance = db.Column(db.Float, nullable=False)
    paid_amount_gpay = db.Column(db.Float, nullable=False)
    paid_amount_cash = db.Column(db.Float, nullable=False)
    # paid_amount = db.Column(db.Float, nullable=False)
    remaining_balance = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    dealer = db.relationship("Dealer_details", backref="billing_records")
    item = db.relationship("Item", backref="billing_records")
    
    @property
    def formatted_date(self):
        return self.timestamp.strftime("%d/%m/%Y")  # Format the date

    @property
    def formatted_time(self):
        return self.timestamp.strftime("%I:%M %p")  # Format the time in 12-hour format

    @property
    def formatted_date_time(self):
        return self.timestamp.strftime("%d-%m-%Y %I:%M %p")

class PaymentBillingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.String(100), db.ForeignKey('dealer_details.dealer_id'))
    credit_balance = db.Column(db.Float, nullable=False)
    paid_amount_gpay = db.Column(db.Float, nullable=False)
    paid_amount_cash = db.Column(db.Float, nullable=False)
    given_amount_gpay = db.Column(db.Float, nullable=False)
    given_amount_cash = db.Column(db.Float, nullable=False)
    remaining_balance = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    dealer = db.relationship("Dealer_details", backref="payment_billing_records")

    @property
    def formatted_date(self):
        return self.timestamp.strftime("%d/%m/%Y")  # Format the date

    @property
    def formatted_time(self):
        return self.timestamp.strftime("%I:%M %p")  # Format the time in 12-hour format

    @property
    def formatted_date_time(self):
        return self.timestamp.strftime("%d-%m-%Y %I:%M %p")

class DailyAccounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    date = db.Column(db.Date, nullable=False, default=date.today)

    one_can_price = db.Column(db.Float, default=0)
    total_can_filling = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    
    total_credit_amount = db.Column(db.Float, default=0)
    today_credit_amount = db.Column(db.Float, default=0)

    amount_gpay = db.Column(db.Float, default=0)
    amount_cash = db.Column(db.Float, default=0)
    net_recevied_amount = db.Column(db.Float, default=0)


    credit_amount_received_gpay = db.Column(db.Float, default=0)
    credit_amount_received_cash = db.Column(db.Float, default=0)
    net_credit_amount_received = db.Column(db.Float, default=0)

    chit_amount = db.Column(db.Float, default=0)
    diesel = db.Column(db.Float, default=0)

    chit_amount = db.Column(db.Float, default=0)
    diesel = db.Column(db.Float, default=0)
    spares = db.Column(db.Float, default=0)
    pooja_items = db.Column(db.Float, default=0)
    milk_and_others = db.Column(db.Float, default=0)
    salary_advance = db.Column(db.Float, default=0)
    salary = db.Column(db.Float, default=0)
    eb = db.Column(db.Float, default=0)
    service_labour = db.Column(db.Float, default=0)
    stationaries = db.Column(db.Float, default=0)
    sunday_ots = db.Column(db.Float, default=0)
    others_expenses = db.Column(db.Float, default=0)
    notes = db.Column(db.String(100), default=0)
    total_expenses = db.Column(db.Float, default=0)

    net_amount_remaining = db.Column(db.Float, default=0)
    net_cash_remaining = db.Column(db.Float, default=0)

    @property
    def formatted_date(self):
        return self.date.strftime("%d-%m-%Y")  # Format the date
    
    @property
    def formatted_date_time(self):
        return self.timestamp.strftime("%d-%m-%Y %I:%M %p")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            session.permanent = True  # THIS activates the lifetime
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/')
def home():
    admin=False
    if 'user' in session:
        admin = True
    return render_template('home.html', admin=admin)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dealer_details')
def dealer_details():
    if 'user' not in session:
        return redirect(url_for("login"))
    dealers = Dealer_details.query.order_by(Dealer_details.name.asc()).all()
    return render_template('dealer_details.html', dealers=dealers)

@app.route('/add_dealer_details', methods=['POST'])
def add_dealer_details():
    dealer_id = request.form['dealer_id']
    name = request.form['name']
    mobile = request.form['mobile']
    address = request.form['address']
    aadhaar_file = request.files.get('aadhaar_file')
    photo_file = request.files.get('photo_file')

    # Check if the dealer_id already exists
    existing_dealer = Dealer_details.query.filter_by(dealer_id=dealer_id).first()

    if existing_dealer:
        flash('Dealer ID already exists!', 'error')
        return redirect(url_for('dealer_details'))

    aadhaar_filename = ''
    photo_filename = ''
    
    if aadhaar_file and allowed_file(aadhaar_file.filename):
        aadhaar_filename = secure_filename(f"{dealer_id}_aadhaar.{aadhaar_file.filename.rsplit('.', 1)[1]}")
        aadhaar_file.save(os.path.join(app.config['UPLOAD_FOLDER'], aadhaar_filename))

    if photo_file and allowed_file(photo_file.filename):
        photo_filename = secure_filename(f"{dealer_id}_photo.{photo_file.filename.rsplit('.', 1)[1]}")
        photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    new_dealer = Dealer_details(dealer_id=dealer_id, name=name, mobile=mobile, address=address, aadhaar_file=aadhaar_filename, photo_file=photo_filename)
    new_account = DealerAccounts(dealer_id=new_dealer.dealer_id, current_balance=0.0)
    db.session.add(new_account)
    db.session.add(new_dealer)
    db.session.commit()
    flash('Dealer added successfully!', 'success')
    return redirect(url_for('dealer_details'))

@app.route('/edit_dealer_details/<int:id>', methods=['POST'])
def edit_dealer_details(id):
    dealer = Dealer_details.query.get_or_404(id)
    dealer.dealer_id = request.form['dealer_id']
    dealer.name = request.form['name']
    dealer.mobile = request.form['mobile']
    dealer.address = request.form['address']
    db.session.commit()
    return redirect(url_for('dealer_details'))

@app.route('/delete_dealer_details/<int:id>')
def delete_dealer_details(id):
    dealer = Dealer_details.query.get_or_404(id)
    db.session.delete(dealer)
    db.session.commit()
    return redirect(url_for('dealer_details'))


@app.route('/data_entry')
def data_entry(error_message=None):
    # Show the main page for entering dealer data and queue
    today = datetime.today().date()
    dealer_queue = db.session.query(Dealer, Dealer_details.name).outerjoin(Dealer_details, Dealer.dealer_id == Dealer_details.dealer_id).filter(func.date(Dealer.timestamp) == today).order_by(Dealer.timestamp.desc()).limit(5).all()
    # for dealer in dealer_queue:
    #     # Assuming `timestamp` is a datetime object, you can format it as required
    #     dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format as hour:minute
    token_no = get_next_token_id()
    return render_template('data_entry.html', queue=dealer_queue, token_no = token_no, error_message=error_message)

@app.route('/update_dealer', methods=['POST'])
def update_dealer():
    dealer_id = request.form.get('dealer_id')
    water_can_count = request.form.get('water_can_count')
    dealer_record_id = request.form.get('dealer_record_id')  # Hidden field with dealer DB ID
    password = request.form.get('password')

    correct_password = edit_password  # Set your password here

    if password != correct_password:
        return {"status": "error", "message": "Incorrect password!"}, 403

    dealer = Dealer.query.get(dealer_record_id)
    if dealer:
        dealer.dealer_id = dealer_id
        dealer.water_can_count = int(water_can_count)
        db.session.commit()
        return {"status": "success", "message": "Dealer details updated!"}
    
    return {"status": "error", "message": "Dealer not found!"}, 404

def get_total_can_today():
    #Total Can
    query = Dealer.query
    start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Filter data from today only
    query = query.filter(Dealer.timestamp >= start_of_today)
    filtered_data = query.order_by(Dealer.timestamp.desc()).all()
    total_cans = sum(dealer.water_can_count for dealer in filtered_data)
    return total_cans

@app.route('/dashboard')
def dashboard():
    # Show the main page for entering dealer data and queue
    today = datetime.today().date()
    dealer_queue = db.session.query(Dealer, Dealer_details.name).outerjoin(Dealer_details, Dealer.dealer_id == Dealer_details.dealer_id).filter(func.date(Dealer.timestamp) == today).order_by(Dealer.timestamp.desc()).limit(5).all()
        # Format the timestamp to show only hours and minutes
    # for dealer in dealer_queue:
    #     # Assuming `timestamp` is a datetime object, you can format it as required
    #     dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M")  # Format as hour:minute
    
    return render_template('dashboard.html', queue=dealer_queue, total_cans=get_total_can_today())

@app.route('/add_dealer', methods=['POST'])
def add_dealer():
    dealer_id = request.form.get('dealer_id')
    water_can_count = request.form.get('water_can_count')
    token_no = request.form.get('token_no')
    
    if dealer_id and water_can_count.isdigit() and token_no:
        water_can_count = int(water_can_count)
        
        token_no = int(token_no)

        # Check if the token number is already used for today
        today = datetime.today().date()
        existing_token = Dealer.query.filter_by(token_id=token_no).filter(func.date(Dealer.timestamp) == today).first()

        if existing_token:
            # Token already exists, redirect with error message
            error_message = f"Token number {token_no} has already been assigned for today."
            return data_entry(error_message) 

        # Create a new dealer entry with token_id
        new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count, token_id=token_no)

        db.session.add(new_dealer)
        db.session.commit()
        if is_sms_required:
            threading.Thread(target=send_message,args=(dealer_id,water_can_count,)).start()
    threading.Thread(target=token_updated_send_to_esp32,args=(get_next_token_id(),)).start()
    return redirect(url_for('data_entry'))

@app.route('/add_dealer_esp32', methods=['POST'])
def add_dealer_esp32():
    status = "failed"
    try:
        dealer_id = request.form.get('dealer_id')
        water_can_count = request.form.get('water_can_count')
        token_no = request.form.get('token_no')
        # print(token_no)
        if dealer_id and water_can_count.isdigit() and token_no:
            water_can_count = int(water_can_count)
            
            token_no = int(token_no)

            # Check if the token number is already used for today
            today = datetime.today().date()
            existing_token = Dealer.query.filter_by(token_id=token_no).filter(func.date(Dealer.timestamp) == today).first()

            if existing_token:
                # Token already exists, redirect with error message
                error_message = "existing_token"
                return error_message
                
            # Create a new dealer entry with token_id
            new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count, token_id=token_no)

            db.session.add(new_dealer)
            db.session.commit()
            status = "success"
            if is_sms_required:
                threading.Thread(target=send_message,args=(dealer_id,water_can_count,)).start()
    except Exception as e:
        print(f"Error in esp post request reciving: {e}")

    token_updated_send_to_website_ui()

    return status

def token_updated_send_to_esp32(token_id):
    try:
        esp32_url = f"http://{esp32_ip}/{esp32_api}"
        data = {"message": token_id}
        response = requests.get(esp32_url, params=data)
        print(f"Token sent ESP response: {response.text}")
    except Exception as e:
        print(f"Error sending token to esp32: {e}")

def token_updated_send_to_website_ui():
    pass

def add_dealer_from_display(dealer_id, water_can_count):
    if dealer_id and water_can_count.isdigit():
        water_can_count = int(water_can_count)

        # Create a new dealer entry with token_id
        new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count, token_id=get_next_token_id())

        db.session.add(new_dealer)
        db.session.commit()

# def get_next_token_id():
#     today = datetime.today().date()
#     # Get the last entry for today
#     last_entry = Dealer.query.filter(func.date(Dealer.timestamp)==today).order_by(Dealer.id.desc()).first()
#     # last_entry_today = Dealer.query.filter_by(date=datetime.utcnow().date()).first()
#     print(last_entry)
#     last_token_id = last_entry.token_id if last_entry else 0
#     # Increment the token ID, resetting to 1 every 50 counts
#     token_id = (last_token_id % token_id_reset_value) + 1
#     return token_id

@app.route('/get_tokenId_esp32', methods=['POST'])
def get_next_token_id_esp32():
    return str(get_next_token_id())

def get_next_token_id():
    today = datetime.today().date()
    
    # Get all token IDs for today, sorted in ascending order
    tokens_today = Dealer.query.with_entities(Dealer.token_id)\
        .filter(func.date(Dealer.timestamp) == today)\
        .order_by(Dealer.token_id.asc())\
        .all()
    
    # Extract token IDs into a flat list
    token_ids = [token[0] for token in tokens_today]
    max_token_id = max(token_ids) if len(token_ids)>0 else 0
    for i in range(1, max_token_id + 2):
        if i not in token_ids:
            return i
    
    # If no gaps are found, start over at 1
    return 1

def get_filtered_data(request, is_daily_monthly_report=False):
        # Retrieve filter values from the request arguments
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    filter_button = request.args.get('filter_button', '')
    
    # Get filter parameters
    if is_daily_monthly_report:
        filter_type = request.args.get('filter_type', '1-month')  # Options: '1day', '1month', or 'all'
    else:   
        filter_type = request.args.get('filter_type', '1-day')  # Options: '1day', '1month', or 'all'

    # Start a query to fetch data from the database
    # query = Dealer.query
    if is_daily_monthly_report:
        query = db.session.query(
            func.date(Dealer.timestamp).label('date'),
            func.sum(Dealer.water_can_count).label('total_cans')
        )
    else:
        query = db.session.query(Dealer, Dealer_details.name).outerjoin(Dealer_details, Dealer.dealer_id == Dealer_details.dealer_id)
    # Apply filters if provided
    if dealer_id_filter:
        query = query.filter(Dealer.dealer_id == dealer_id_filter)
    
    if filter_button:
        if date_from:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Dealer.timestamp >= date_from_dt)
        
        if date_to:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # query = query.filter(Dealer.timestamp <= date_to_dt+timedelta(days=1))
            query = query.filter(Dealer.timestamp <= date_to_dt)
        
        filter_type = "all"

    else:
        # Apply date filters based on the selected filter type
        if filter_type == '1-day':
            # Get today's start time (midnight)
            start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # Filter data from today only
            query = query.filter(Dealer.timestamp >= start_of_today)

            # threshold_date = datetime.now() - timedelta(days=1)
            # query = query.filter(Dealer.timestamp >= threshold_date)
        elif filter_type == '1-month':
            # threshold_date = datetime.now() - timedelta(days=30)
            # query = query.filter(Dealer.timestamp >= threshold_date)
            now = datetime.now()
            first_day_of_month = datetime(now.year, now.month, 1)
            query = query.filter(Dealer.timestamp >= first_day_of_month)
                    
    if is_daily_monthly_report:
        filtered_data = query.group_by(func.date(Dealer.timestamp)).order_by(func.date(Dealer.timestamp)).all()
    else:
        filtered_data = query.order_by(Dealer.timestamp.desc()).all()

    return filtered_data, filter_type

@app.route('/history', methods=['GET'])
def history(msg=None):
    if 'user' not in session:
        return redirect(url_for("login"))
    filtered_data, filter_type = get_filtered_data(request)
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    # filter_button = request.args.get('filter_button', '')
    
    # if dealer_id_filter == "" and date_from == "" and date_to == "":
    #     filtered_data = query.order_by(Dealer.timestamp.desc()).limit(20).all()
    
    total_cans = sum(dealer.water_can_count for dealer, dealer_name in filtered_data)
    
    # for dealer in filtered_data:
    #     # Assuming `timestamp` is a datetime object, you can format it as required
    #     dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format as hour:minute
    
    # Render the history template and pass the filters to retain their values

    return render_template('history.html', data=filtered_data, 
                            dealer_id=dealer_id_filter, 
                            date_from=date_from, 
                            date_to=date_to,
                            total_cans=total_cans, 
                            filter_type=filter_type,
                            msg=msg)

#filter options are hided.
@app.route('/history-mini', methods=['GET'])
def history_mini(msg=None):
    filtered_data, filter_type = get_filtered_data(request)
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    # filter_button = request.args.get('filter_button', '')
    
    # if dealer_id_filter == "" and date_from == "" and date_to == "":
    #     filtered_data = query.order_by(Dealer.timestamp.desc()).limit(20).all()
    
    total_cans = sum(dealer.water_can_count for dealer, dealer_name in filtered_data)
    
    # for dealer in filtered_data:
    #     # Assuming `timestamp` is a datetime object, you can format it as required
    #     dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format as hour:minute
    
    # Render the history template and pass the filters to retain their values

    return render_template('history-mini.html', data=filtered_data, 
                            dealer_id=dealer_id_filter, 
                            date_from=date_from, 
                            date_to=date_to,
                            total_cans=total_cans, 
                            filter_type=filter_type,
                            msg=msg)
#Dealer accounts
@app.route('/dealer_accounts')
def dealer_accounts():
    dealers = get_filtered_data_dealer_account(request)
    # dealers = Dealer_details.query.outerjoin(DealerAccounts, Dealer_details.dealer_id == DealerAccounts.dealer_id).add_entity(DealerAccounts).order_by(Dealer_details.name.asc()).all()
    return render_template("dealer_accounts.html", dealers=dealers)

@app.route('/update_payment/<dealer_id>', methods=['POST'])
def update_payment(dealer_id):
    amount_paid_gpay = float(request.form.get('amount_paid_gpay',0))
    amount_paid_cash = float(request.form.get('amount_paid_cash',0))
    due_amount_given_gpay = float(request.form.get('due_amount_given_gpay',0))
    due_amount_given_cash = float(request.form.get('due_amount_given_cash',0))
    amount_paid = amount_paid_gpay + amount_paid_cash
    due_amount_given = due_amount_given_gpay + due_amount_given_cash

    account = DealerAccounts.query.filter_by(dealer_id=dealer_id).first()
    current_credit_balance = account.current_balance
    if account:
        if amount_paid!=0:
            account.current_balance -= amount_paid
        if due_amount_given!=0:
            account.current_balance += due_amount_given
        account.last_payment_date = datetime.now()
    else:
        # if account doesn't exist yet, create it
        if amount_paid!=0:
            account = DealerAccounts(dealer_id=dealer_id, current_balance=-amount_paid, last_payment_date=datetime.now())
        if due_amount_given!=0:
            account = DealerAccounts(dealer_id=dealer_id, current_balance=+due_amount_given, last_payment_date=datetime.now())
        db.session.add(account)
    db.session.commit()

    payment_bill = PaymentBillingHistory(
        dealer_id=dealer_id,
        credit_balance=current_credit_balance,
        paid_amount_gpay=amount_paid_gpay,
        paid_amount_cash=amount_paid_cash,
        given_amount_gpay=due_amount_given_gpay,
        given_amount_cash=due_amount_given_cash,
        remaining_balance=account.current_balance
    )
    db.session.add(payment_bill)
    db.session.commit()

    return print_payment_bill(payment_bill.id, "/dealer_accounts")

def get_filtered_data_dealer_account(request):
    # Retrieve filter values from the request arguments
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    filter_button = request.args.get('filter_button', '')
    
    query = db.session.query(Dealer_details, DealerAccounts).outerjoin(DealerAccounts, Dealer_details.dealer_id == DealerAccounts.dealer_id)
    # Apply filters if provided
    if filter_button and dealer_id_filter:
        query = query.filter(Dealer_details.dealer_id == dealer_id_filter)
    
    filtered_data = query.order_by(Dealer_details.name.asc()).all()

    return filtered_data

#Item management
@app.route('/item_management', methods=['GET', 'POST'])
def item_management():
    if 'user' not in session:
        return redirect(url_for("login"))
    if request.method == 'POST':
        item_id = request.form['item_id']

        # Check if the dealer_id already exists
        existing_item = Item.query.filter_by(item_id=item_id).first()
        if existing_item:
            flash('Item ID already exists!', 'error')
            return redirect(url_for('item_management'))
        
        item_name = request.form['item_name']
        price = round(float(request.form['price']),2)
        new_item = Item(item_id=item_id, item_name=item_name, price=price)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('item_management'))
    
    all_items = Item.query.all()
    return render_template('item_management.html', items=all_items)

@app.route('/edit_item/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    # item.item_id = request.form['item_id']
    # # Check if the dealer_id already exists
    # existing_item = Item.query.filter_by(item_id=item.item_id).first()
    # if existing_item:
    #     flash('Item ID already exists!', 'error')
    #     return redirect(url_for('item_management'))

    item.item_name = request.form['item_name']
    item.price = float(request.form['price'])
    flash('Item added successfully!', 'success')
    db.session.commit()
    return redirect(url_for('item_management'))

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    # Check if the dealer_id already exists
    existing_item = Item.query.filter_by(id=item_id).first()
    print(existing_item.item_id)
    if existing_item.item_id==default_item_id:
        flash('Default Item cannot be delete!', 'error')
        return redirect(url_for('item_management'))

    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('item_management'))

#Material management
@app.route('/material_management', methods=['GET', 'POST'])
def material_management():
    if request.method == 'POST':   
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        shop_name = request.form['shop_name']
        total = request.form['total']
        amount_paid = request.form['amount_paid']
        date = request.form['date']
        new_material = Material(name=name, price=price, quantity=quantity, shop_name=shop_name, total=total, amount_paid=amount_paid, date=date)
        db.session.add(new_material)
        db.session.commit()
        flash('Material added successfully!', 'success')
        return redirect(url_for('material_management'))
    
    all_material = Material.query.all()
    return render_template('material_management.html', materials=all_material)

@app.route('/edit_material/<int:material_id>', methods=['POST'])
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    material.name = request.form['name']
    material.price = request.form['price']
    material.quantity = request.form['quantity']
    material.shop_name = request.form['shop_name']
    material.total = request.form['total']
    material.amount_paid = request.form['amount_paid']
    material.date = request.form['date']
    flash('Material added successfully!', 'success')
    db.session.commit()
    return redirect(url_for('material_management'))

@app.route('/delete_material/<int:material_id>', methods=['POST'])
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully!', 'success')
    return redirect(url_for('material_management'))

#Daily accounts
@app.route('/daily_accounts', methods=['GET', 'POST'])
def daily_accounts():
    if request.method == 'POST':
        data = request.form
        # Get all fields from form
        date_str = request.form.get('date')
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            entry_date = date.today()

        one_can_price = float(data.get('one_can_price', 0))
        total_can_filling = float(data.get('total_can_filling', 0))
        total_amount = float(data.get('total_amount', 0))
        total_can_filling = float(data.get('total_can_filling', 0))
        total_credit_amount = float(data.get('total_credit_amount', 0))
        today_credit_amount = float(data.get('today_credit_amount', 0))
        amount_gpay = float(data.get('amount_gpay', 0))
        amount_cash = float(data.get('amount_cash', 0))
        net_recevied_amount = float(data.get('net_recevied_amount', 0))
        credit_amount_received_gpay = float(data.get('credit_amount_received_gpay', 0))
        credit_amount_received_cash = float(data.get('credit_amount_received_cash', 0))
        net_credit_amount_received = float(data.get('net_credit_amount_received', 0))
        chit_amount = float(data.get('chit_amount', 0))
        diesel = float(data.get('diesel', 0))
        spares = float(data.get('spares', 0))
        pooja_items = float(data.get('pooja_items', 0))
        milk_and_others = float(data.get('milk_and_others', 0))
        salary_advance = float(data.get('salary_advance', 0))
        salary = float(data.get('salary', 0))
        eb = float(data.get('eb', 0))
        service_labour = float(data.get('service_labour', 0))
        stationaries = float(data.get('stationaries', 0))
        sunday_ots = float(data.get('sunday_ots', 0))
        others_expenses = float(data.get('others_expenses', 0))
        notes = data.get('notes',"")
        total_expenses = float(data.get('total_expenses_2', 0))
        net_amount_remaining = float(data.get('net_amount_remaining', 0))
        net_cash_remaining = float(data.get('net_cash_remaining', 0))

        record = DailyAccounts(
            date=entry_date,
            one_can_price=one_can_price,
            total_can_filling=total_can_filling,
            total_amount=total_amount,
            total_credit_amount=total_credit_amount,
            today_credit_amount=today_credit_amount,
            amount_gpay=amount_gpay,
            amount_cash=amount_cash,
            net_recevied_amount=net_recevied_amount,
            credit_amount_received_gpay=credit_amount_received_gpay,
            credit_amount_received_cash=credit_amount_received_cash,
            net_credit_amount_received=net_credit_amount_received,
            chit_amount=chit_amount,
            diesel=diesel,
            spares=spares,
            pooja_items=pooja_items,
            milk_and_others=milk_and_others,
            salary_advance=salary_advance,
            salary=salary,
            eb=eb,
            service_labour=service_labour,
            stationaries=stationaries,
            sunday_ots=sunday_ots,
            others_expenses=others_expenses,
            notes=notes,
            total_expenses=total_expenses,
            net_amount_remaining=net_amount_remaining,
            net_cash_remaining=net_cash_remaining
        )
        
        db.session.add(record)
        db.session.commit()
        flash("Daily Statement saved!", "success")
        return redirect(url_for('daily_accounts'))
        
    today_date = date.today().isoformat()

    today = datetime.today().date()
    dealer = Dealer.query.filter(func.date(Dealer.timestamp)==today).all()
    billingHistory = BillingHistory.query.filter(func.date(BillingHistory.timestamp)==today).all()
    paymentBillingHistory = PaymentBillingHistory.query.filter(func.date(PaymentBillingHistory.timestamp)==today).all()
    item = Item.query.filter_by(item_id=default_item_id).first()

    one_can_price = item.price
    total_can_filling = sum([dealer_row.water_can_count for dealer_row in dealer])
    total_amount = one_can_price * total_can_filling
    total_credit_amount = sum([row.remaining_balance for row in billingHistory])
    
    amount_gpay = sum([row.paid_amount_gpay for row in billingHistory])
    amount_cash = sum([row.paid_amount_cash for row in billingHistory])
    net_recevied_amount = amount_gpay + amount_cash

    credit_amount_received_gpay = sum([row.paid_amount_gpay for row in paymentBillingHistory])
    credit_amount_received_cash = sum([row.paid_amount_cash for row in paymentBillingHistory])
    net_credit_amount_received = credit_amount_received_gpay + credit_amount_received_cash

    today_credit_amount = total_amount - net_recevied_amount

    return render_template('daily_accounts.html', today_date=today_date, one_can_price=one_can_price, total_can_filling=total_can_filling, total_amount=total_amount,
                           total_credit_amount=total_credit_amount, amount_gpay=amount_gpay, amount_cash=amount_cash, net_recevied_amount=net_recevied_amount, credit_amount_received_gpay=credit_amount_received_gpay, credit_amount_received_cash=credit_amount_received_cash, net_credit_amount_received=net_credit_amount_received, today_credit_amount=today_credit_amount)

def get_filtered_data_daily_accounts(request):
    # Retrieve filter values from the request arguments
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    filter_button = request.args.get('filter_button', '')

    query = DailyAccounts.query

    if filter_button:

        if date_from:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(DailyAccounts.date >= date_from_dt)

        if date_to:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # query = query.filter(DailyAccounts.date <= date_to_dt+timedelta(days=1))
            query = query.filter(DailyAccounts.date <= date_to_dt)
    else:
        # Get 1 month Details
        now = datetime.now()
        first_day_of_month = datetime(now.year, now.month, 1)
        query = query.filter(DailyAccounts.date >= first_day_of_month)
        pass

    filtered_data = query.order_by(DailyAccounts.timestamp.desc()).all()

    return filtered_data

@app.route('/monthly_statement', methods=['GET', 'POST'])
def monthly_statement():
    filtered_data = get_filtered_data_daily_accounts(request)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    return render_template('monthly_statement.html', date_from=date_from, date_to=date_to, statements=filtered_data)

@app.route('/edit_monthly_statement/<int:statement_id>', methods=['POST'])
def edit_monthly_statement(statement_id):
    dailyAccounts = DailyAccounts.query.get_or_404(statement_id)

    dailyAccounts.chit_amount = float(request.form['chit_amount'])
    dailyAccounts.diesel = float(request.form['diesel'])
    dailyAccounts.spares = float(request.form['spares'])
    dailyAccounts.pooja_items = float(request.form['pooja_items'])
    dailyAccounts.milk_and_others = float(request.form['milk_and_others'])
    dailyAccounts.salary_advance = float(request.form['salary_advance'])
    dailyAccounts.salary = float(request.form['salary'])
    dailyAccounts.eb = float(request.form['eb'])
    dailyAccounts.service_labour = float(request.form['service_labour'])
    dailyAccounts.stationaries = float(request.form['stationaries'])
    dailyAccounts.sunday_ots = float(request.form['sunday_ots'])
    dailyAccounts.others_expenses = float(request.form['others_expenses'])
    dailyAccounts.notes = request.form['notes']
    dailyAccounts.total_expenses = float(request.form['total_expenses'])
    dailyAccounts.net_amount_remaining = float(request.form['net_amount_remaining'])
    dailyAccounts.net_cash_remaining = float(request.form['net_cash_remaining'])

    flash('Daily Statement Edited successfully!', 'success')
    db.session.commit()
    return redirect(url_for('monthly_statement'))

@app.route('/delete_monthly_statement/<int:statement_id>', methods=['POST'])
def delete_monthly_statement(statement_id):
    dailyAccounts = DailyAccounts.query.get_or_404(statement_id)
    db.session.delete(dailyAccounts)
    db.session.commit()
    flash('Daily Statement deleted successfully!', 'success')
    return redirect(url_for('monthly_statement'))

@app.route('/export_monthly_statement')
def export_monthly_statement_data():
    filtered_data = get_filtered_data_daily_accounts(request)
    output, filename = generate_excel_monthly_statement(filtered_data)

    return send_file(output, download_name=filename, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# Function to generate Excel
def generate_excel_monthly_statement(data):
    # dealers = Dealer.query.all()

    excel_data = {
        "ID": [d.id for d in data],
        "One Can Price": [d.one_can_price for d in data],
        "Total Can Filling": [d.total_can_filling for d in data],
        "Total Amount": [d.total_amount  for d in data],
        "Total Credits Amount": [d.total_credit_amount for d in data],
        "Today Credits Amount": [d.today_credit_amount for d in data],
        "Amount received (Gpay)": [d.amount_gpay for d in data],
        "Amount received (Cash)": [d.amount_cash for d in data],
        "Net Amount Received": [d.net_recevied_amount for d in data],
        "Credit Amount received (Gpay)": [d.credit_amount_received_gpay for d in data],
        "Credit Amount received (Cash)": [d.credit_amount_received_cash for d in data],
        "Net Credit Amount Received": [d.credit_amount_received_cash for d in data],
        "Chit Amount": [d.chit_amount for d in data],
        "Dieselt": [d.diesel for d in data],
        "Spares": [d.spares for d in data],
        "Pooja Items": [d.pooja_items for d in data],
        "Milk and Others": [d.milk_and_others for d in data],
        "Salary Advance": [d.salary_advance for d in data],
        "Salary": [d.salary for d in data],
        "Eb": [d.eb for d in data],
        "Service Labour": [d.service_labour for d in data],
        "Stationaries": [d.stationaries for d in data],
        "Sunday Ots": [d.sunday_ots for d in data],
        "Others Expenses": [d.others_expenses for d in data],
        "Notes": [d.notes for d in data],
        "Total Expense": [d.total_expenses for d in data],
        "Net Amount Remaining": [d.net_amount_remaining for d in data],
        "Amount received (Gpay)(-)": [d.amount_gpay for d in data],
        "Net Cash Remaining": [d.net_cash_remaining for d in data],
        "Date": [d.formatted_date for d in data],
        "Time Stamp": [d.formatted_date_time for d in data],
    }
    
    df = pd.DataFrame(excel_data)

    # Generate a filename with the current date and time
    timestamp = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    filename = f"Monthly_report_data_{timestamp}.xlsx"
    filepath = os.path.join("exports", filename)
    # Ensure the 'exports' folder exists
    if not os.path.exists("exports"):
        os.makedirs("exports")

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Billing History Data")

    return filepath, filename


#Billing
@app.route('/billing')
def billing():
    # Show the main page for entering dealer data and queue
    today = datetime.today().date()
    dealer_queue = db.session.query(Dealer, Dealer_details.name, BillingHistory.id).outerjoin(Dealer_details, Dealer.dealer_id == Dealer_details.dealer_id).outerjoin(BillingHistory, and_(Dealer.token_id == BillingHistory.billing_id, func.date(Dealer.timestamp) == func.date(BillingHistory.timestamp))).filter(func.date(Dealer.timestamp) == today).order_by(Dealer.timestamp.desc()).all()
    return render_template('billing.html', queue=dealer_queue, total_cans=get_total_can_today())

@app.route('/generate_bill/<token_id>', methods=['GET', 'POST'])
def generate_bill(token_id):
    today = datetime.today().date()
    dealer = Dealer.query.filter(func.date(Dealer.timestamp)==today).filter_by(token_id=token_id).first()
    dealer_id = dealer.dealer_id
    dealer_details = Dealer_details.query.filter_by(dealer_id=dealer_id).first()
    account = DealerAccounts.query.filter_by(dealer_id=dealer_id).first()
    item = Item.query.filter_by(item_id=default_item_id).first()

    if request.method == 'POST':
        quantity = dealer.water_can_count
        paid_amount_gpay = round(float(request.form['paid_amount_gpay']), 2)
        paid_amount_cash = round(float(request.form['paid_amount_cash']), 2)
        grand_total = round(quantity * item.price, 2)
        total_amount = round(grand_total / (1 + gst_rate), 2)
        gst_amount = round(grand_total - total_amount, 2)

        remaining_balance = round((account.current_balance or 0) + grand_total - paid_amount_gpay - paid_amount_cash, 2)

        bill = BillingHistory(
            billing_id=dealer.token_id,
            dealer_id=dealer_id,
            item_id=item.id,
            quantity=quantity,
            item_price=item.price,
            total_amount=total_amount,
            gst_amount=gst_amount,
            grand_total=grand_total,
            credit_balance=account.current_balance,
            paid_amount_gpay=paid_amount_gpay,
            paid_amount_cash=paid_amount_cash,
            remaining_balance=remaining_balance
        )

        db.session.add(bill)
        account.current_balance = remaining_balance
        db.session.commit()
        return print_bill(bill.id, "/billing")

    return render_template('generate_bill.html', dealer=dealer, dealer_details=dealer_details, item=item, account=account)

def  get_filtered_data_billing(request):
    # Retrieve filter values from the request arguments
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    filter_button = request.args.get('filter_button', '')

    query = BillingHistory.query

    if filter_button:
        if dealer_id_filter:
            query = query.filter(BillingHistory.dealer_id == dealer_id_filter)
        
        if date_from:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(BillingHistory.timestamp >= date_from_dt)

        if date_to:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # query = query.filter(BillingHistory.timestamp <= date_to_dt+timedelta(days=1))
            query = query.filter(BillingHistory.timestamp <= date_to_dt)
    else:
        # Get today's start time (midnight)
        start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Filter data from today only
        query = query.filter(BillingHistory.timestamp >= start_of_today)

    filtered_data = query.order_by(BillingHistory.timestamp.desc()).all()

    return filtered_data

@app.route('/billing_history')
def billing_history():
    if 'user' not in session:
        return redirect(url_for("login"))
    filtered_data = get_filtered_data_billing(request)
    dealer_id = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    return render_template('billing_history.html', dealer_id=dealer_id, date_from=date_from, date_to=date_to, filtered_data=filtered_data, bills=filtered_data)

@app.route('/export_billing_history')
def export_billing_history_data():
    filtered_data = get_filtered_data_billing(request)
    output, filename = generate_excel_billing_history(filtered_data)

    return send_file(output, download_name=filename, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route('/print_bill/<int:id>/<path:return_path>')
def print_bill(id, return_path):
    bill = BillingHistory.query.filter_by(id=id).first()
    dealer = bill.dealer
    item = bill.item
    return render_template('print_bill.html', bill=bill, dealer=dealer, item=item, return_path=return_path)


#payment billing
def  get_filtered_data_payment_billing(request):
    # Retrieve filter values from the request arguments
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    filter_button = request.args.get('filter_button', '')

    query = PaymentBillingHistory.query

    if filter_button:
        if dealer_id_filter:
            query = query.filter(PaymentBillingHistory.dealer_id == dealer_id_filter)
        
        if date_from:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(PaymentBillingHistory.timestamp >= date_from_dt)

        if date_to:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            # query = query.filter(PaymentBillingHistory.timestamp <= date_to_dt+timedelta(days=1))
            query = query.filter(PaymentBillingHistory.timestamp <= date_to_dt)
    else:
        # Get today's start time (midnight)
        start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Filter data from today only
        query = query.filter(PaymentBillingHistory.timestamp >= start_of_today)

    filtered_data = query.order_by(PaymentBillingHistory.timestamp.desc()).all()

    return filtered_data

@app.route('/payment_billing_history')
def payment_billing_history():
    if 'user' not in session:
        return redirect(url_for("login"))
    filtered_data = get_filtered_data_payment_billing(request)
    dealer_id = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    return render_template('payment_billing_history.html', dealer_id=dealer_id, date_from=date_from, date_to=date_to, filtered_data=filtered_data, payment_bill=filtered_data)

@app.route('/export_payment_billing_history')
def export_payment_billing_history_data():
    filtered_data = get_filtered_data_payment_billing(request)
    output, filename = generate_excel_payment_billing_history(filtered_data)

    return send_file(output, download_name=filename, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route('/print_payment_bill/<int:id>/<path:return_path>')
def print_payment_bill(id,return_path):
    payment_bill = PaymentBillingHistory.query.filter_by(id=id).first()
    dealer = payment_bill.dealer
    return render_template('print_payment_bill.html', payment_bill=payment_bill, dealer=dealer, return_path=return_path)

@app.route('/bill_generated')
def bill_generated():
    flash("Bill generated successfully!", "success")
    return redirect(url_for('billing'))


# Function to generate Excel
def generate_excel_billing_history(dealers):
    # dealers = Dealer.query.all()
    data = {
        "ID": [d.id for d in dealers],
        "Billing Id": [d.billing_id for d in dealers],
        "Dealer Id": [d.dealer_id for d in dealers],
        "Dealer Name": [d.dealer.name  for d in dealers],
        "Item Name": [d.item.item_name for d in dealers],
        "Quantity": [d.quantity for d in dealers],
        "Item price": [d.item_price for d in dealers],
        "Total Amount": [d.total_amount for d in dealers],
        "Gst Amount": [d.gst_amount for d in dealers],
        "Grand Total": [d.grand_total for d in dealers],
        "Credit Amount": [d.credit_amount for d in dealers],
        "Paid Amount(Gpay)": [d.paid_amount_gpay for d in dealers],
        "Paid Amount(Cash)": [d.paid_amount_cash for d in dealers],
        "Remaining Balance": [d.remaining_balance for d in dealers],
        "Time": [d.formatted_date_time for d in dealers],
    }
    
    df = pd.DataFrame(data)

    # Generate a filename with the current date and time
    timestamp = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    filename = f"billing_history_data_{timestamp}.xlsx"
    filepath = os.path.join("exports", filename)
    # Ensure the 'exports' folder exists
    if not os.path.exists("exports"):
        os.makedirs("exports")

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Billing History Data")

    return filepath, filename

# Function to generate Excel
def generate_excel_payment_billing_history(dealers):
    # dealers = Dealer.query.all()
    data = {
        "ID": [d.id for d in dealers],
        "Dealer Id": [d.dealer_id for d in dealers],
        "Dealer Name": [d.dealer.name  for d in dealers],
        "Credit Amount": [d.credit_balance for d in dealers],
        "Paid Amount(Gpay)": [d.paid_amount_gpay for d in dealers],
        "Paid Amount(Cash)": [d.paid_amount_cash for d in dealers],
        "Given Amount(Gpay)": [d.given_amount_gpay for d in dealers],
        "Given Amount(Cash)": [d.given_amount_cash for d in dealers],
        "Remaining Balance": [d.remaining_balance for d in dealers],
        "Time": [d.formatted_date_time for d in dealers],
    }
    
    df = pd.DataFrame(data)

    # Generate a filename with the current date and time
    timestamp = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    filename = f"payment_billing_history_data_{timestamp}.xlsx"
    filepath = os.path.join("exports", filename)
    # Ensure the 'exports' folder exists
    if not os.path.exists("exports"):
        os.makedirs("exports")

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Payment Billing History Data")

    return filepath, filename


# Function to generate Excel
def generate_excel(dealers):
    # dealers = Dealer.query.all()
    data = {
        "Token ID": [d.token_id for d, dealer_name in dealers],
        "Dealer ID": [d.dealer_id for d, dealer_name in dealers],
        "Name": [dealer_name for d, dealer_name in dealers],
        "Water Cans": [d.water_can_count for d, dealer_name in dealers],
        "Date": [d.timestamp.strftime("%d-%m-%Y") for d, dealer_name in dealers],
        "Time": [d.timestamp.strftime("%I:%M %p") for d, dealer_name in dealers]  # 12-hour format
    }
    
    df = pd.DataFrame(data)

    # Calculate total cans
    total_cans = df["Water Cans"].sum()

    # Add an empty row and total row at the end
    total_row = pd.DataFrame([{ "Token ID": "", "Dealer ID": "TOTAL", "Water Cans": total_cans, "Date": "", "Time": ""}])
    df = pd.concat([df, pd.DataFrame([{}]), total_row], ignore_index=True)

    # Generate a filename with the current date and time
    timestamp = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    filename = f"dealers_data_{timestamp}.xlsx"
    filepath = os.path.join("exports", filename)
    # Ensure the 'exports' folder exists
    if not os.path.exists("exports"):
        os.makedirs("exports")

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Dealers Data")

    return filepath, filename

def generate_excel_monthly_report(entry):
    # dealers = Dealer.query.all()
    data = {
        "S. No": [i for i in range(1,len(entry)+1)],
        "Date": [e.date for e in entry],
        "Total can": [e.total_cans for e in entry]  # 12-hour format
    }
    
    df = pd.DataFrame(data)

    # Calculate total cans
    total_cans = df["Total can"].sum()

    # Add an empty row and total row at the end
    total_row = pd.DataFrame([{ "S. No": "", "Date": "TOTAL", "Total can": total_cans,}])
    df = pd.concat([df, pd.DataFrame([{}]), total_row], ignore_index=True)

    # Generate a filename with the current date and time
    timestamp = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
    filename = f"dealers_data_{timestamp}.xlsx"
    filepath = os.path.join("exports", filename)
    # Ensure the 'exports' folder exists
    if not os.path.exists("exports"):
        os.makedirs("exports")

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Dealers Data")

    return filepath, filename


# Route to download Excel
@app.route('/export')
def export_data():
    report_type = request.args.get('report_type', '') 
    if report_type=="monthly_report":
        filtered_data, filter_type = get_filtered_data(request,True)
        output, filename = generate_excel_monthly_report(filtered_data)
    else:
        filtered_data, filter_type = get_filtered_data(request)
        output, filename = generate_excel(filtered_data)

    return send_file(output, download_name=filename, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Route to send Excel via email
@app.route('/send_email')
def send_email():
    recipient_email = request.args.get('email')

    if not recipient_email:
        return "Email is required!", 400
    
    filtered_data, filter_type = get_filtered_data(request)
    output, filename = generate_excel(filtered_data)
    with open(output, 'rb') as f:
        file_data = f.read()

    msg = Message("Dealers Data Report", sender=email_id, recipients=[recipient_email])
    msg.body = "Attached is the dealer data report in Excel format."

    # Attach Excel file
    msg.attach(filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", file_data)

    mail.send(msg)

    return history("Email sent successfully!!!")

def daily_mail_api():
    query = db.session.query(Dealer, Dealer_details.name).outerjoin(Dealer_details, Dealer.dealer_id == Dealer_details.dealer_id)

    start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    query = query.filter(Dealer.timestamp >= start_of_today)

    filtered_data = query.order_by(Dealer.timestamp.desc()).all()
    output, filename = generate_excel(filtered_data)
    with open(output, 'rb') as f:
        file_data = f.read()

    msg = Message("Dealers Data Report", sender=email_id, recipients=[daily_mail_email_id])
    msg.body = "Attached is the dealer data report in Excel format."

    # Attach Excel file
    msg.attach(filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", file_data)

    mail.send(msg)

@app.route('/inactive_dealers', methods=['GET', 'POST'])
def inactive_dealers():
    days = 30
    inactive_dealers = []

    if request.method == 'POST':
        days = int(request.form.get('days', 0))
    threshold_date = datetime.now() - timedelta(days=days)

    # Get dealers who haven't visited since the threshold date
    inactive_dealers = db.session.query(Dealer, Dealer_details).outerjoin(Dealer, Dealer.dealer_id == Dealer_details.dealer_id).group_by(Dealer.dealer_id).having(
        db.func.max(Dealer.timestamp) < threshold_date
    ).all()
    #print(inactive_dealers)
    return render_template('inactive_dealers.html', inactive_dealers=inactive_dealers, days=days)

@app.route('/monthly_report')
def monthly_report():
    if 'user' not in session:
        return redirect(url_for("login"))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
  
    filtered_data, filter_type = get_filtered_data(request, True)
    # Group by date and get total cans
    daily_summary = filtered_data

    # Calculate grand total
    grand_total = sum([entry.total_cans for entry in daily_summary])
    # for entry in daily_summary:
    #     entry.date = entry.date.strftime('%d-%m-%Y')

    return render_template('monthly_report.html', daily_summary=daily_summary, grand_total=grand_total, date_from=date_from, 
                            date_to=date_to,)

# WhatsApp numbers: 'from_' is your Twilio Sandbox number
def send_whatsapp_message():
    try:
        with app.app_context():
            message = client.messages.create(
                from_="whatsapp:"+twilio_whatsapp_number,  # Twilio sandbox number
                body="Hi,\nTotal cans refilled today: "+str(get_total_can_today()),
                to='whatsapp:+91'+msg_gopi_send_number  # Replace with your number
            )
            print(f"Message sent! SID: {message.sid}")
    except Exception as e:
        print(f"Error: {e}")
        
def send_daily_message_scheduled():
    try:
        with app.app_context():
            message = client.messages.create(
                from_=twilio_number,  # Twilio sandbox number
                body="Hi,\nTotal cans refilled today: "+str(get_total_can_today()),
                to=msg_gopi_send_number  # Replace with your number
            )
            print(f"Message sent! SID: {message.sid}")
    except Exception as e:
        print(f"Error: {e}")

def send_message(dealer_id, water_can_count):
    try:
        with app.app_context():
            dealer = Dealer_details.query.filter_by(dealer_id=dealer_id).first()

            if dealer:
                name = dealer.name
                mobile = dealer.mobile
                mobile = mobile.split(",")[0].strip()
                if mobile:
                    mobile = "+91"+mobile

                    msg="Hi "+str(name)+", Water can loading in progress."
                    with app.app_context():
                        message = client.messages.create(
                            from_=twilio_number,  # Twilio sandbox number
                            body=msg,
                            to=mobile  # Replace with your number
                        )
                        print(f"Message sent! SID: {message.sid}")
                else:
                    print(f"Message Not sent! Delaer details not found")
    except Exception as e:
        print(f"Error: {e}")

def send_to_blynk():
    while True:
        with app.app_context():
            today_can_count = get_total_can_today()
            url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH_TOKEN}&{VIRTUAL_PIN}={today_can_count}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # print(f"[{datetime.now()}] Sent count {today_can_count} to Blynk!")
                    pass
                else:
                    print(f"[{datetime.now()}] Failed to send: {response.status_code}")
                    pass
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(10)

def schedule_task():
    # 🕒 Schedule the message
    if is_sms_required:
        schedule.every().day.at(schedule_time_1).do(send_daily_message_scheduled)
        schedule.every().day.at(schedule_time_2).do(send_daily_message_scheduled)
    schedule.every().day.at(daily_report_schedule_time).do(daily_mail_api)
    print(f"Scheduled task at {schedule_time_1} and {schedule_time_2} and {daily_report_schedule_time}. Waiting...")
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(1)

#the below is just one time run code to populate data
def generate_dealer_account_table():
    # Go through all existing dealers
    dealers = Dealer_details.query.all()

    for dealer in dealers:
        # Check if account already exists
        account = DealerAccounts.query.filter_by(dealer_id=dealer.dealer_id).first()
        if not account:
            # Create with default balance = 0
            new_account = DealerAccounts(dealer_id=dealer.dealer_id, current_balance=0.0)
            db.session.add(new_account)

    db.session.commit()
    
if __name__ == '__main__':
    # Initialize the database (create tables)
    with app.app_context():
        db.create_all()
        #generate_dealer_account_table() #Run to createa account for existing dealers
        threading.Thread(target=token_updated_send_to_esp32,args=(get_next_token_id(),)).start() #send the token on startup
        threading.Thread(target=schedule_task).start() #send the token on startup
        threading.Thread(target=send_to_blynk).start() #send the token on startup

    if is_rashberrypi: 
        pass
        # from display_functions import start_display_functions
        # t = threading.Thread(target=start_display_functions)
        # t.start()
    app.run(host='0.0.0.0', port="5000", debug=debug_mode)
    if is_rashberrypi:
        pass
        # t.join()
        