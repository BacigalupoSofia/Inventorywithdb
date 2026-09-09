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

#Main page of the app

@app.route('/')
def home():
    return render_template('home.html')

# display of Stock in the dental practice 

@app.route('/stock', methods=['GET', 'POST'])
def stock():

    products = Product.query.all() 
    return render_template('index.html', products=products)

# Add new product to the stock

@app.route('/add', methods=['GET', 'POST'])
def add_product():

    if request.method == 'POST':
    
            name = request.form['name']
            description = request.form['description']
            manufacturer = request.form['manufacturer']
            stock_quantity = int(request.form['quantity'])
    
            new_product = Product(
                name=name,
                description=description,
                manufacturer=manufacturer,
                stock_quantity=stock_quantity,
            )
            db.session.add(new_product)
            db.session.commit()
    
            return redirect(url_for('stock'))
    return render_template('add.html')

# Delete from database or add or remove 1 item from the stock quantity 

@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('stock'))

@app.route('/minus/<int:id>')
def minus_stock(id):
    product = Product.query.get_or_404(id)
    product.stock_quantity -= 1
    db.session.commit()
    return redirect(url_for('stock'))

@app.route('/plus/<int:id>')
def plus_stock(id):

    product = Product.query.get_or_404(id)
    product.stock_quantity += 1
    db.session.commit()
    return redirect(url_for('stock'))


# View product details

@app.route('/details/<int:id>')
def details(id):
    product = Product.query.get_or_404(id)
    return render_template('details.html', product=product)

# Edit product

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.manufacturer = request.form['manufacturer']
        product.stock_quantity = int(request.form['stock_quantity'])

        db.session.commit()
        return redirect(url_for('stock'))

    return render_template('edit.html', product=product)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)