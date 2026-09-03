from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(50), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        manufacturer = request.form['manufacturer']
        stock_quantity = int(request.form['quantity'])

        new_product = Product(name=name, description=description, manufacturer=manufacturer, stock_quantity=stock_quantity)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('home'))

    products = Product.query.all() 
    return render_template('index.html', products=products)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)