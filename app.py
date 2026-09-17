from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Product, Provider, Order, OrderItem, Link
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = "my-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Main page of the app

@app.route('/')
def home():
    return render_template('home.html')

#PRODUCTS ROUTES -------------------------------------------------------------

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
        link = request.form['link']
        image = request.files['image']

        if image and image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.static_folder,'uploads',filename))
        else:
                filename = 'nophotoavailable.jpg'
                

        new_product = Product(
            name=name,
            description=description,
            manufacturer=manufacturer,
            stock_quantity=stock_quantity,
            provider_id=provider_id,
            img=filename
        )

        db.session.add(new_product)
        db.session.flush()

        new_product_link = Link(
            link = link,
            product_id = new_product.id,
            provider_id = provider_id
        )

        db.session.add(new_product_link)
        db.session.commit()

        flash( f"{new_product.name} added to the list.", "product_added")

        return redirect(url_for('stock'))

    return render_template(
        'add.html',
        providers=providers
    )


# Delete from database or add or remove 1 item from the stock quantity 

@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    order_item = OrderItem.query.filter_by(product_id=product.id).first() 

    if order_item: 
        flash( f"Cannot delete {product.name} because it is already in an order.", "product_deleted" ) 
        return redirect(url_for('stock'))

    db.session.delete(product)
    flash( f"{product.name} deleted", "product_deleted")
        
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
    product_link = Link.query.filter_by(product_id=product.id, provider_id=product.provider_id).first()

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.manufacturer = request.form['manufacturer']
        product.stock_quantity = int(request.form['stock_quantity'])


        if product_link:
            product_link.link= request.form['link']
        else:
            product_link = Link(
            link=request.form['link'],
            product_id=product.id,
            provider_id=product.provider_id)

            db.session.add(product_link)

        db.session.commit()

        flash( f"{product.name} has been edited", "product_edited")

        return redirect(url_for('stock'))

    return render_template('edit.html', product=product, product_link=product_link)


#PROVIDERS CRUD -------------------------------------------------------------

# Add providers if not exist
@app.route('/providers/add', methods=['GET', 'POST'])
def add_provider():

    if request.method == 'POST':

        name = request.form['name']
        website = request.form['website']

        new_provider = Provider(
            name=name,
            website=website
        )

        existing = Provider.query.filter_by(name = new_provider.name).first()

        if not existing:
            db.session.add(new_provider)
            db.session.commit()


        return redirect(url_for('provider_list'))

    return render_template('add_provider.html')

@app.route('/providers/seed')
def seed_data():
    # Seed providers

    main_providers = [
        {'name':'Dontalia', 'website':'https://www.dontalia.com/'},
        {'name':'Henry Schein', 'website':'https://www.henryschein.ie/'},
        {'name':'DMI', 'website':'https://www.dmi.ie/'},
        {'name':'BF Mulholland', 'website':'https://www.bfmulholland.com/'}
    ]

    for seed in main_providers:
        existing = Provider.query.filter_by(name = seed['name'] ).first()

        if not existing:
            provider = Provider(name=seed['name'], website=seed['website'])
            db.session.add(provider)
            db.session.commit()


    providers=Provider.query.all()

    return render_template('providers.html', providers=providers)

#Display all the existing providers
@app.route('/providers')
def provider_list():

    providers = Provider.query.all()

    return render_template(
        'providers.html',
        providers=providers
    )

# Delete provider (allowed only if not supplying any product)
@app.route('/delete_provider/<int:provider_id>')
def delete_provider(provider_id):

    provider_del = Provider.query.get_or_404(provider_id)

    if provider_del.products:
        product_names = ", ".join(
            product.name for product in provider_del.products
        )

        message = (
            f"Cannot delete {provider_del.name}. "
            f"They supply: {product_names}"
        )

        flash(message, "error")

        return redirect(url_for('provider_list'))

    db.session.delete(provider_del)
    db.session.commit()

    flash(
        f"{provider_del.name} was deleted successfully.",
        "success"
    )

    return redirect(url_for('provider_list'))

# ORDERS ROUTES ------------------------------------------------------------------------------

@app.route('/my_orders')
def my_orders():
    orders = Order.query.all()

    return render_template('order_plan.html', orders=orders)

#change status clicking
@app.route('/toggle_order_status/<int:order_id>')
def toggle_order_status(order_id):

    order = Order.query.get_or_404(order_id)

    if order.status == "Planning":
        order.status = "Waiting"

    elif order.status == "Waiting":
        order.status = "Completed"

    elif order.status == "Completed":
        order.status = "Planning"

    db.session.commit()

    return redirect(url_for('my_orders'))

# PRODUCTS IN ORDERS ROUTES ------------------------------------------------------------------

@app.route('/add_to_order/<int:product_id>')
def add_to_order(product_id):

    product = Product.query.get_or_404(product_id)

    # 1. are we planning any order with the provider of this product?
    order = Order.query.filter_by(
        provider_id=product.provider_id,
        status="Planning"
    ).first()

    # create a new order
    if not order:
        order = Order(
            provider_id=product.provider_id,
            status="Planning"
        )

        db.session.add(order)
        db.session.commit()

    # 2. Is the product is already in the order
    order_item = OrderItem.query.filter_by(
        order_id=order.id,
        product_id=product.id
    ).first()
    # add up 1 unit or add the product for first time
    if order_item:
        order_item.quantity += 1

        flash(
            f"Another unit of {product.name} added to the order.",
            "order_success"
        )

    else:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1
        )

        db.session.add(order_item)

        flash(
            f"{product.name} added to the order.",
            "order_success"
        )

    db.session.commit()

    return redirect(url_for('my_orders'))

@app.route('/delete_from_order/<int:unwanted_item_id>')
def delete_from_order(unwanted_item_id):

    unwanted_item = OrderItem.query.get_or_404(unwanted_item_id)

    db.session.delete(unwanted_item)
    db.session.commit()

    return redirect(url_for('my_orders'))

@app.route('/minus_order/<int:id>')
def minus_order(id):

    product = OrderItem.query.get_or_404(id)
    product.quantity -= 1

    if product.quantity == 0:
        db.session.delete(product)
        
    db.session.commit()
    
    return redirect(url_for('my_orders'))

    
@app.route('/plus_order/<int:id>')
def plus_order(id):

    product = OrderItem.query.get_or_404(id)
    product.quantity += 1
    db.session.commit()

    return redirect(url_for('my_orders'))
    



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)