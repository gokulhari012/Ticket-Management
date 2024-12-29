from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dealers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    return render_template('home.html', queue=dealer_queue)

@app.route('/add_dealer', methods=['POST'])
def add_dealer():
    dealer_id = request.form.get('dealer_id')
    water_can_count = request.form.get('water_can_count')

    if dealer_id and water_can_count.isdigit():
        water_can_count = int(water_can_count)

         # Get the current date
        today = datetime.now().date()

        # Check the highest token_id for today's entries
        max_token = db.session.query(func.max(Dealer.token_id)).filter(
            func.date(Dealer.timestamp) == today).scalar()

        token_id = (max_token or 0) + 1  # Increment token ID or start at 1

        # Create a new dealer entry with token_id
        new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count, token_id=token_id)

        db.session.add(new_dealer)
        db.session.commit()

    return redirect(url_for('home'))

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
    
    # Fetch filtered data
    filtered_data = query.order_by(Dealer.timestamp.desc()).all()

    # Render the history template and pass the filters to retain their values
    return render_template('history.html', data=filtered_data, 
                           dealer_id=dealer_id_filter, 
                           date_from=date_from, 
                           date_to=date_to)

if __name__ == '__main__':
    # Initialize the database (create tables)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
