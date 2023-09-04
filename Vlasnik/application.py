import io
import json

from flask import Flask, Response, request
from models import *
from configuration import Configuration
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity, get_jwt
import csv
from sqlalchemy import func,or_

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/", methods=["GET"])
def index():
    return "Dobrodsli vlasnice!"


@application.route("/update", methods=["POST"])
@jwt_required()
def update():
    # role_check
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'vlasnik' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)
    # end_of_role_check

    try:
        content = request.files["file"].stream.read().decode("utf-8")
    except KeyError:
        return Response(json.dumps({
            "message": "Field file is missing."
        }), status=400)
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    num_lines = 0
    for row in reader:
        if len(row) != 3:
            return Response(json.dumps({
                "message": f"Incorrect number of values on line {num_lines}."
            }), status=400)

        try:
            price = float(row[2])
            if price <= 0:
                return Response(json.dumps({
                    "message": f"Incorrect price on line {num_lines}."
                }), status=400)
        except ValueError:
            return Response(json.dumps({
                "message": f"Incorrect price on line {num_lines}."
            }), status=400)

        existing_product = Product.query.filter_by(name=row[1]).first()
        if existing_product:
            name = existing_product.name
            return Response(json.dumps({
                "message": f"Product {name} already exists."
            }), status=400)
        num_lines += 1

    stream = io.StringIO(content)
    reader = csv.reader(stream)

    for row in reader:
        categories = row[0].split("|")
        for cat in categories:
            existing_category = Category.query.filter_by(name = cat).first()
            if not existing_category:
                new_category = Category(name=cat)
                database.session.add(new_category)
                database.session.commit()

        product_name = row[1]
        product_price= row[2]
        new_product = Product(name=product_name, price=product_price)
        database.session.add(new_product)
        database.session.commit()

        for cat in categories:
            category_object = Category.query.filter_by(name=cat).first()
            link = ProductCategory(productId=new_product.id, categoryId=category_object.id)
            database.session.add(link)
            database.session.commit()

    return Response(status=200)


@application.route("/product_statistics", methods=["GET"])
@jwt_required()
def product_statistics():
    # role_check
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'vlasnik' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)
    # end_of_role_check

    prod_stats = {}
    for product in Product.query.all():
        num_of_sold = ProductOrder.query\
            .join(Order, ProductOrder.orderId==Order.id)\
            .filter(ProductOrder.productId==product.id, or_(Order.status=="COMPLETE", Order.status=="PENDING")) \
            .with_entities(func.sum(ProductOrder.quantity).label('sold_count')) \
            .scalar()

        num_of_waiting = ProductOrder.query\
            .join(Order, ProductOrder.orderId==Order.id)\
            .filter(
                ProductOrder.productId==product.id,
                Order.status=="CREATED"
            )\
            .with_entities(func.sum(ProductOrder.quantity).label("wait_count"))\
            .scalar()

        nums = {
            "sold": int(num_of_sold or 0),
            "waiting": int(num_of_waiting or 0)
        }
        if nums["sold"] == 0 and nums["waiting"] == 0:
            continue
        prod_stats[product] = nums

    res_arr = []
    for k, v in prod_stats.items():
        res_arr.append({
            "name": k.name,
            "sold": v["sold"],
            "waiting": v["waiting"]
        })

    return Response(json.dumps({"statistics": res_arr}), status=200)


@application.route("/category_statistics", methods=["GET"])
@jwt_required()
def category_statistics():
    # role_check
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'vlasnik' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)
    # end_of_role_check

    stats_per_category = {}
    all_categories = Category.query.all()
    for category in all_categories:
        num_products_sold = ProductCategory.query\
            .join(Product, Product.id==ProductCategory.productId)\
            .join(ProductOrder, ProductOrder.productId == Product.id)\
            .join(Order, Order.id == ProductOrder.orderId)\
            .filter(ProductCategory.categoryId==category.id, or_(Order.status=="COMPLETE", Order.status=="PENDING")) \
            .with_entities(func.sum(ProductOrder.quantity).label('sold_count')) \
            .scalar()
        num_sold = int(num_products_sold or 0)

        num_products_waiting = ProductCategory.query \
            .join(Product, Product.id == ProductCategory.productId) \
            .join(ProductOrder, ProductOrder.productId == Product.id) \
            .join(Order, Order.id == ProductOrder.orderId) \
            .filter(ProductCategory.categoryId == category.id,
                    Order.status=="CREATED") \
            .with_entities(func.sum(ProductOrder.quantity).label('wait_count')) \
            .scalar()

        num_wati = int(num_products_waiting or 0)

        stats_per_category[category.name] = {
            "sold": num_sold,
            "wait": num_wati
        }

    arr = []
    for k,v in stats_per_category.items():
        arr.append({
            "category": k,
            "sold": v["sold"],
            "wait": v["wait"]
        })
    sorted_data = sorted(arr, key=lambda x: (-x["sold"], x["category"]))
    sorted_categories = [item["category"] for item in sorted_data]

    return Response(json.dumps({"statistics": sorted_categories}), status=200)



if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=5001, host="0.0.0.0")