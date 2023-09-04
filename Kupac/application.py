import json

from flask import Flask, request, Response
from configuration import Configuration
from models import *
from flask_jwt_extended import jwt_required, JWTManager, get_jwt, get_jwt_identity
from web3 import Web3, exceptions, HTTPProvider, Account


application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)
web3 = Web3(HTTPProvider("http://ganache-cli:8545"))
og_address = {}

@application.route("/search", methods=["GET"])
@jwt_required()
def search():
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kupac' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)
    # end_of_role_check

    product_name    = request.args.get("name", "")
    category_name   = request.args.get("category", "")
    print(f"{product_name}")

    category_query  = Category.query.filter(Category.name.like(f"%{category_name}%")).all()
    temp = {}
    for cat in category_query:
        temp[cat] = []
        pk = ProductCategory.query.filter_by(categoryId=cat.id).all()
        for p in pk:
            product = Product.query.filter_by(id=p.productId).first()
            if not product_name:
                temp[cat].append(product)
            elif product_name.lower() in product.name.lower():
                temp[cat].append(product)
    print(temp)

    empty_cat = []
    for k, v in temp.items():
        if len(v) == 0:
            empty_cat.append(k)

    for cat in empty_cat:
        del temp[cat]

    print(temp)
    categories_to_return = list(temp.keys())
    categories_to_return_string = [it.name for it in categories_to_return]
    print(categories_to_return_string)

    product_categories = {}
    for values in temp.values():
        for prod in values:
            cats = ProductCategory.query.filter_by(productId = prod.id).all()
            product_categories[prod] = []
            for categ in cats:
                product_categories[prod].append(Category.query.filter_by(id=categ.categoryId).first().name)

    print (categories_to_return_string)
    print(product_categories)

    json_prod_arr = []
    for prod_obj, categories in product_categories.items():
        data = {
            "categories": categories,
            "id": prod_obj.id,
            "name": prod_obj.name,
            "price": prod_obj.price
        }
        json_prod_arr.append(data)

    result = {
        "categories": categories_to_return_string,
        "products": json_prod_arr
    }
    return Response(json.dumps(result), status=200)


@application.route("/order", methods=["POST"])
@jwt_required()
def order():
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kupac' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)

    email = get_jwt_identity()
    print(email)
    products_wanted = request.json.get("requests", "")
    if not products_wanted:
        return Response(json.dumps({"message": "Field requests is missing."}), status=400)

    total_price = 0.0
    products = []
    quantities = []
    num_prod = 0

    for product in products_wanted:
        try:
            id_ = product["id"]
        except KeyError:
            return Response(json.dumps({"message": f"Product id is missing for request number {num_prod}."}),
                            status=400)
        try:
            quantity = product["quantity"]
        except KeyError:
            return Response(json.dumps({"message": f"Product quantity is missing for request number {num_prod}."}),
                            status=400)

        if not isinstance(id_, int) or id_ <= 0:
            return Response(json.dumps({"message": f"Invalid product id for request number {num_prod}."}),
                            status=400)

        if not isinstance(quantity, int) or quantity <= 0:
            return Response(json.dumps({"message": f"Invalid product quantity for request number {num_prod}."}),
                            status= 400)

        prod = Product.query.filter_by(id=id_).first()
        if not prod:
            return Response(json.dumps({"message": f"Invalid product for request number {num_prod}."}),
                            status=400)

        total_price += prod.price * quantity
        num_prod += 1
        products.append(prod)
        quantities.append(quantity)

    customer_address = request.json.get("address", "")
    if not customer_address:
        return Response(json.dumps({"message": "Field address is missing."}), status=400)
    if len(customer_address) < 42:
        return Response(json.dumps({"message": "Invalid address."}), status=400)
    contract = web3.eth.contract(bytecode=Configuration.CONTRACT_BYTECODE, abi=Configuration.CONTRACT_ABI)

    owner_acc = web3.eth.accounts[0]

    transaction_hash = contract.constructor(customer_address, int(total_price)).transact({
        "from": owner_acc
    })
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    contract_address = receipt.contractAddress

    new_order = Order(status="CREATED", price=total_price, user=email, contract=contract_address)

    database.session.add(new_order)
    database.session.commit()

    og_address[new_order.id] = customer_address

    for i in range(len(products)):
        p_o = ProductOrder(productId=products[i].id, orderId=new_order.id, quantity=quantities[i])
        database.session.add(p_o)
        database.session.commit()

    return Response(json.dumps({"id": new_order.id}), status=200)


@application.route("/status", methods=["GET"])
@jwt_required()
def status():
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kupac' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)

    email = get_jwt_identity()
    orders = Order.query.filter_by(user=email).all()

    products_per_order = {}
    for order_obj in orders:
        p_o_arr = ProductOrder.query.filter_by(orderId=order_obj.id).all()
        products_per_order[order_obj] = {}
        for p_o in p_o_arr:
            quantity = p_o.quantity
            product = Product.query.filter_by(id=p_o.productId).first()
            products_per_order[order_obj][product] = quantity

    print(products_per_order)

    json_order_arr = []
    for order_key in products_per_order.keys():
        json_prod_arr = []
        for product_value in products_per_order[order_key]:
            categories = Category.query.join(ProductCategory, Category.id == ProductCategory.categoryId)\
                .filter(ProductCategory.productId == product_value.id).all()
            c_strings = [c.name for c in categories]
            data = {
                "categories": c_strings,
                "name": product_value.name,
                "price": product_value.price,
                "quantity": products_per_order[order_key][product_value]
            }
            json_prod_arr.append(data)
        json_order_arr.append({
            "products": json_prod_arr,
            "price": order_key.price,
            "status": order_key.status,
            "timestamp": str(order_key.time)
        })

    return Response(json.dumps({"orders": json_order_arr}), status=200)


@application.route("/delivered", methods=["POST"])
@jwt_required()
def delivered():
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kupac' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)

    try:
        order_id = request.json.get("id", "")

        if not order_id and order_id != 0:
            return Response(json.dumps({"message": "Missing order id."}),
                            status=400)
        if order_id <= 0:
            return Response(json.dumps({"message": "Invalid order id."}),
                            status=400)
    except TypeError or ValueError:
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    existing_order = Order.query.filter_by(id=order_id).first()

    if not existing_order:
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    if existing_order.status == "CREATED":
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    keys = request.json.get("keys", "")
    if not keys:
        return Response(json.dumps({"message": "Missing keys."}),
                        status=400)

    phrase = request.json.get("passphrase", "")
    if not phrase:
        return Response(json.dumps({"message": "Missing passphrase."}),
                        status=400)

    if isinstance(keys, str):
        try:
            keys = json.loads(keys)
        except json.decoder.JSONDecodeError:
            keys_str = keys.replace("'", "\"")
            keys = json.loads(keys_str)

    try:
        address = web3.to_checksum_address(keys["address"])
        private_key = Account.decrypt(keys, phrase).hex()
    except ValueError:
        return Response(json.dumps({"message": "Invalid credentials."}),
                        status=400)

    contract_address = existing_order.contract
    contract = web3.eth.contract(address=contract_address, abi=Configuration.CONTRACT_ABI)
    contract_status = contract.functions.getState().call()

    if og_address[order_id] != address:
        return Response(json.dumps({"message": "Invalid customer account."}),
                        status=400)

    if contract_status == 0:
        return Response(json.dumps({"message": "Transfer not complete."}),
                        status=400)
    if contract_status == 1:
        return Response(json.dumps({"message": "Delivery not complete."}),
                        status=400)

    transaction = contract.functions.delivered().build_transaction({
        "from": address,
        "nonce": web3.eth.get_transaction_count(address),
        "gasPrice": web3.eth.gas_price
    })

    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    existing_order.status = "COMPLETE"
    database.session.commit()

    return Response(status=200)


@application.route("/pay", methods=["POST"])
@jwt_required()
def pay():
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kupac' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)
    try:
        order_id = request.json.get("id", "")

        if not order_id and order_id != 0:
            return Response(json.dumps({"message": "Missing order id."}),
                            status=400)
        if order_id <= 0:
            return Response(json.dumps({"message": "Invalid order id."}),
                            status=400)
    except TypeError or ValueError:
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    existing_order = Order.query.filter_by(id=order_id).first()
    if not existing_order:
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    keys = request.json.get("keys", "")
    if not keys:
        return Response(json.dumps({"message": "Missing keys."}),
                        status=400)
    phrase = request.json.get("passphrase", "")
    if not phrase:
        return Response(json.dumps({"message": "Missing passphrase."}),
                        status=400)

    if isinstance(keys, str):
        keys = json.loads(keys)

    try:
        address = web3.to_checksum_address(keys["address"])
        private_key = Account.decrypt(keys, phrase).hex()
    except ValueError:
        return Response(json.dumps({"message": "Invalid credentials."}),
                        status=400)

    contract_address = existing_order.contract
    existing_contract = web3.eth.contract(address=contract_address, abi=Configuration.CONTRACT_ABI)
    price = existing_order.price

    if existing_contract.functions.getState().call() >= 1:
        return Response(json.dumps({"message": "Transfer already complete."}),
                        status=400)

    try:
        transaction = existing_contract.functions.pay().build_transaction({
        "from": address,
        "nonce": web3.eth.get_transaction_count(address),
        "gasPrice": web3.eth.gas_price,
        "value": int(price)
        })
        signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
        transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    except ValueError:
        return Response(json.dumps({"message": "Insufficient funds."}),
                        status=400)

    return Response(status=200)

@application.route("/", methods=["GET"])
def index():
    return f"Connected: {web3.is_connected()}"



if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=5003, host="0.0.0.0")
    web3 = Web3(HTTPProvider("http://ganache-cli:8545"))