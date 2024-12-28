from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
        new_dealer = Dealer(dealer_id=dealer_id, water_can_count=water_can_count)

        db.session.add(new_dealer)
        db.session.commit()

    return redirect(url_for('home'))

@app.route('/history', methods=['GET', 'POST'])
def history():
    # Filter data if a dealer_id filter is applied
    dealer_id_filter = request.args.get('dealer_id')
    if dealer_id_filter:
        filtered_data = Dealer.query.filter_by(dealer_id=dealer_id_filter).all()
    else:
        filtered_data = Dealer.query.all()

    return render_template('history.html', data=filtered_data)

if __name__ == '__main__':
    # Initialize the database (create tables)
    with app.app_context():
        db.create_all()

    app.run(debug=True)