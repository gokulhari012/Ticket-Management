from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
import threading

edit_password = "lotus@123"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dealers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# token_id_reset_value = 50

# is_rashberrypi = True
is_rashberrypi = False

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

@app.route('/data_entry')
def data_entry(error_message=None):
    # Show the main page for entering dealer data and queue
    dealer_queue = Dealer.query.order_by(Dealer.timestamp.desc()).limit(5).all()
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

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    # Show the main page for entering dealer data and queue
    dealer_queue = Dealer.query.order_by(Dealer.timestamp.desc()).limit(5).all()
        # Format the timestamp to show only hours and minutes
    # for dealer in dealer_queue:
    #     # Assuming `timestamp` is a datetime object, you can format it as required
    #     dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M")  # Format as hour:minute
    
    return render_template('dashboard.html', queue=dealer_queue)

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

    return redirect(url_for('data_entry'))

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

def get_next_token_id():
    today = datetime.today().date()
    
    # Get all token IDs for today, sorted in ascending order
    tokens_today = Dealer.query.with_entities(Dealer.token_id)\
        .filter(func.date(Dealer.timestamp) == today)\
        .order_by(Dealer.token_id.asc())\
        .all()
    
    # Extract token IDs into a flat list
    token_ids = [token[0] for token in tokens_today]
    for i in range(1, max(token_ids) + 2):
        if i not in token_ids:
            return i
    
    # If no gaps are found, start over at 1
    return 1

@app.route('/history', methods=['GET'])
def history():
    # Retrieve filter values from the request arguments
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    filter_button = request.args.get('filter_button', '')
    
    # Get filter parameters
    filter_type = request.args.get('filter_type', '1-month')  # Options: '1day', '1month', or 'all'

    # Start a query to fetch data from the database
    query = Dealer.query

    # Apply filters if provided
    if dealer_id_filter:
        query = query.filter(Dealer.dealer_id == dealer_id_filter)
    
    if filter_button:
        if date_from:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Dealer.timestamp >= date_from_dt)
        
        if date_to:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Dealer.timestamp <= date_to_dt)
        
        filter_type = "all"

    else:
        # Apply date filters based on the selected filter type
        if filter_type == '1-day':
            threshold_date = datetime.now() - timedelta(days=1)
            query = query.filter(Dealer.timestamp >= threshold_date)
        elif filter_type == '1-month':
            threshold_date = datetime.now() - timedelta(days=10)
            query = query.filter(Dealer.timestamp >= threshold_date)
        


    filtered_data = query.order_by(Dealer.timestamp.desc()).all()

    # if dealer_id_filter == "" and date_from == "" and date_to == "":
    #     filtered_data = query.order_by(Dealer.timestamp.desc()).limit(20).all()
    
    total_cans = sum(dealer.water_can_count for dealer in filtered_data)
    
    # for dealer in filtered_data:
    #     # Assuming `timestamp` is a datetime object, you can format it as required
    #     dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format as hour:minute
    
    # Render the history template and pass the filters to retain their values

    return render_template('history.html', data=filtered_data, 
                            dealer_id=dealer_id_filter, 
                            date_from=date_from, 
                            date_to=date_to,
                            total_cans=total_cans, 
                            filter_type=filter_type)



@app.route('/inactive_dealers', methods=['GET', 'POST'])
def inactive_dealers():
    days = 30
    inactive_dealers = []

    if request.method == 'POST':
        days = int(request.form.get('days', 0))
    threshold_date = datetime.now() - timedelta(days=days)

    # Get dealers who haven't visited since the threshold date
    inactive_dealers = db.session.query(Dealer.dealer_id).group_by(Dealer.dealer_id).having(
        db.func.max(Dealer.timestamp) < threshold_date
    ).all()

    return render_template('inactive_dealers.html', inactive_dealers=inactive_dealers, days=days)


if __name__ == '__main__':
    # Initialize the database (create tables)
    with app.app_context():
        db.create_all()
    if is_rashberrypi: 
        from display_functions import start_display_functions
        t = threading.Thread(target=start_display_functions)
        t.start()
    app.run(host='0.0.0.0', port="80", debug=True)
    if is_rashberrypi:
        t.join()
        