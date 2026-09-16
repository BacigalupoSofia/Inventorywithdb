from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(50), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    provider = db.relationship('Provider', back_populates='products')

    order_items = db.relationship(
        "OrderItem",
        back_populates="product"
    )

    links = db.relationship(
        'Link',
        back_populates='product')

    def __repr__(self):
        return f'<Product {self.name}>'


## MODEL TO ADD LINK TO THE PROVIDER PAGE FOR THAT PRODUCT
class Link(db.Model):
    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id'),
        nullable=False
    )

    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)

    product = db.relationship(
        'Product',
        back_populates='links'
    )

    provider = db.relationship('Provider', back_populates='links')


    def __repr__(self):
        return f'<Product {self.id}>'

#Providers model. 
#Each product has exactly one provider. A provider can supply many products.

class Provider(db.Model):
    __tablename__ = 'providers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(100), nullable=False)

    products = db.relationship('Product', back_populates='provider')
    

    orders = db.relationship(
        "Order",
        back_populates="provider"
    )

    links = db.relationship(
    'Link',
    back_populates='provider'
)

    def __repr__(self):
            return f'<Provider {self.name}>'


# Order model is OVERALL ORDER PLAN with provider and status 
# One provider can provide multiple products in the same order,
# One product can be orderer multiple times in the order. 

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20),nullable=False,default="Planning")

    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)

    provider = db.relationship("Provider",back_populates="orders")
    items = db.relationship("OrderItem",back_populates="order",cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id}>'

    # OrderItem is the model for the next stock replenishment (the products within each order)

class OrderItem(db.Model):
        __tablename__ = 'order_items'

        id = db.Column(db.Integer, primary_key=True)
        order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
        product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
        quantity = db.Column(db.Integer, nullable=False)

        order = db.relationship("Order",back_populates="items")
        product = db.relationship("Product",back_populates="order_items")

        def __repr__(self):
            return f"<OrderItem {self.product.name} x {self.quantity}>"