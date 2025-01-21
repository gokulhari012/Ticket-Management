from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dealers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

token_id_reset_value = 50

# is_rashberrypi = True
is_rashberrypi = False

# Database model for dealer data
class Dealer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.String(100), nullable=False)
    water_can_count = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    token_id = db.Column(db.Integer, nullable=False)  # Daily resetting token ID

    def __repr__(self):
        return f'<Dealer {self.dealer_id}>'

@app.route('/')
def home():
    # Show the main page for entering dealer data and queue
    dealer_queue = Dealer.query.order_by(Dealer.timestamp.desc()).limit(5).all()
    for dealer in dealer_queue:
        # Assuming `timestamp` is a datetime object, you can format it as required
        dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format as hour:minute
    
    return render_template('home.html', queue=dealer_queue)

@app.route('/dashboard')
def dashboard():
    # Show the main page for entering dealer data and queue
    dealer_queue = Dealer.query.order_by(Dealer.timestamp.desc()).limit(5).all()
        # Format the timestamp to show only hours and minutes
    for dealer in dealer_queue:
        # Assuming `timestamp` is a datetime object, you can format it as required
        dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M")  # Format as hour:minute
    
    return render_template('dashboard.html', queue=dealer_queue)

@app.route('/add_dealer', methods=['POST'])
def add_dealer():
    dealer_id = request.form.get('dealer_id')
    water_can_count = request.form.get('water_can_count')

    if dealer_id and water_can_count.isdigit():
        water_can_count = int(water_can_count)

        # Create a new dealer entry with token_id
        new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count, token_id=get_next_token_id())

        db.session.add(new_dealer)
        db.session.commit()

    return redirect(url_for('home'))

def add_dealer_from_display(dealer_id, water_can_count):
    if dealer_id and water_can_count.isdigit():
        water_can_count = int(water_can_count)

        # Create a new dealer entry with token_id
        new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count, token_id=get_next_token_id())

        db.session.add(new_dealer)
        db.session.commit()

def get_next_token_id():
    today = datetime.today().date()
    # Get the last entry for today
    last_entry = Dealer.query.filter(func.date(Dealer.timestamp)==today).order_by(Dealer.id.desc()).first()
    print(last_entry)
    last_token_id = last_entry.token_id if last_entry else 0
    # Increment the token ID, resetting to 1 every 50 counts
    token_id = (last_token_id % token_id_reset_value) + 1
    return token_id

@app.route('/history', methods=['GET'])
def history():
    # Retrieve filter values from the request arguments
    dealer_id_filter = request.args.get('dealer_id', '')  # Default is an empty string
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Start a query to fetch data from the database
    query = Dealer.query

    # Apply filters if provided
    if dealer_id_filter:
        query = query.filter(Dealer.dealer_id == dealer_id_filter)
    
    if date_from:
        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Dealer.timestamp >= date_from_dt)
    
    if date_to:
        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Dealer.timestamp <= date_to_dt)

    filtered_data = query.order_by(Dealer.timestamp.desc()).all()

    if dealer_id_filter == "" and date_from == "" and date_to == "":
        filtered_data = query.order_by(Dealer.timestamp.desc()).limit(20).all()

    for dealer in filtered_data:
        # Assuming `timestamp` is a datetime object, you can format it as required
        dealer.timestamp = dealer.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format as hour:minute
    
    # Render the history template and pass the filters to retain their values
    return render_template('history.html', data=filtered_data, 
                           dealer_id=dealer_id_filter, 
                           date_from=date_from, 
                           date_to=date_to)


if __name__ == '__main__':
    # Initialize the database (create tables)
    with app.app_context():
        db.create_all()
    if is_rashberrypi: 
        from display_functions import start_display_functions
        t = threading.Thread(target=start_display_functions)
        t.start()
    app.run(host='0.0.0.0', port="80", debug=False)
    if is_rashberrypi:
        t.join()
        