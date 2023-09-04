from flask_sqlalchemy import SQLAlchemy
import datetime

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "productcategory"

    id = database.Column(database.Integer, primary_key = True)
    productId = database.Column(database.Integer, database.ForeignKey("product.id"), nullable = False)
    categoryId = database.Column(database.Integer, database.ForeignKey("category.id"), nullable = False)


class Category(database.Model):
    __tablename__ = "category"

    id      = database.Column(database.Integer, primary_key = True)
    name    = database.Column(database.String(256), nullable = False)

    products = database.relationship("Product", secondary = ProductCategory.__table__, back_populates = "categories")

    def __repr__(self):
        return f"Category: {self.name}"


class ProductOrder(database.Model):
    __tablename__ = "productorder"

    id          = database.Column(database.Integer, primary_key = True)
    quantity    = database.Column(database.Integer, nullable = False)
    productId   = database.Column(database.Integer, database.ForeignKey("product.id"), nullable = False)
    orderId     = database.Column(database.Integer, database.ForeignKey("order.id"), nullable = False)


class Product(database.Model):
    __tablename__ = "product"

    id      = database.Column(database.Integer, primary_key = True)
    name    = database.Column(database.String(256), nullable = False)
    price   = database.Column(database.Float, nullable = False)

    categories  = database.relationship("Category", secondary = ProductCategory.__table__, back_populates = "products")
    orders      = database.relationship("Order", secondary = ProductOrder.__table__, back_populates = "products")

    def __repr__(self):
        return f"Product: {self.name} - {self.price}"


class Order(database.Model):
    __tablename__ = "order"

    id      = database.Column(database.Integer, primary_key = True)
    price   = database.Column(database.Float, nullable = False)
    status  = database.Column(database.String(16), nullable = False)
    time    = database.Column(database.DateTime(timezone=True), default=datetime.datetime.utcnow)
    user   = database.Column(database.String(256), nullable = False)
    contract = database.Column(database.String(256))

    products = database.relationship("Product", secondary = ProductOrder.__table__, back_populates = "orders")

    def __repr__(self):
        return f"Order: {self.id}, price: {self.price}, status: {self.status}, timestamp: {self.time}, email: {self.user}"