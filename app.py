from flask import Flask, render_template, request, redirect, url_for
from models import db, Product, Provider, Order, OrderItem

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Main page of the app

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

    providers = Provider.query.all()

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        manufacturer = request.form['manufacturer']
        stock_quantity = int(request.form['quantity'])
        provider_id = request.form['provider_id']

        new_product = Product(
            name=name,
            description=description,
            manufacturer=manufacturer,
            stock_quantity=stock_quantity,
            provider_id=provider_id
        )

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('stock'))

    return render_template(
        'add.html',
        providers=providers
    )

# Add providers 

@app.route('/providers/add', methods=['GET', 'POST'])
def add_provider():

    if request.method == 'POST':

        name = request.form['name']
        website = request.form['website']

        new_provider = Provider(
            name=name,
            website=website
        )

        db.session.add(new_provider)
        db.session.commit()

        return redirect(url_for('provider_list'))

    return render_template('add_provider.html')

@app.route('/providers')
def provider_list():

    providers = Provider.query.all()

    return render_template(
        'providers.html',
        providers=providers
    )

@app.route('/seed')
def seed_data():
    # Seed providers

    provider1 = Provider(name='Dontalia', website='https://www.dontalia.com/')
    provider2 = Provider(name='Henry Schein', website='https://www.henryschein.ie/')
    provider3 = Provider(name='DMI', website='https://www.dmi.ie/?srsltid=AfmBOoqxe0ZRU3W1HykxQm6g-Stduc2StDLafUXySfi4X72npXNqW2ce')
    provider4 = Provider(name='BF Mulholland', website='https://www.bfmulholland.com/')

    db.session.add_all([provider1, provider2, provider3, provider4])
    db.session.commit()

    providers=Provider.query.all()

    return render_template('providers.html', providers=providers)

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

    page = request.args.get("page")

    if product.stock_quantity > 0:
        product.stock_quantity -= 1
        db.session.commit()


    if page == "stock":
        return redirect(url_for("stock"))

    if page == "details":
        return redirect(url_for("details", id=id))
    
@app.route('/plus/<int:id>')
def plus_stock(id):

    page = request.args.get("page")

    product = Product.query.get_or_404(id)
    product.stock_quantity += 1
    db.session.commit()
    
    if page == "stock":
        return redirect(url_for("stock"))
    
    if page == "details":
        return redirect(url_for("details", id=id))


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