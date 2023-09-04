import json

from flask import Flask, request, Response
from configuration import Configuration
from flask_jwt_extended import jwt_required, JWTManager, get_jwt
from models import *
from web3 import Web3, HTTPProvider, exceptions, Account

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)
web3 = Web3(HTTPProvider("http://ganache-cli:8545"))


@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
def orders_to_deliver():
    # role_check
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kurir' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)
    # end_of_role_check
    orders = Order.query.filter_by(status="CREATED").all()

    ret_arr = []
    for order in orders:
        data = {
            "id": order.id,
            "email": order.user
        }
        ret_arr.append(data)

    return Response(json.dumps({"orders": ret_arr}), status=200)


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
def pick_up_order():
    # role_check
    current_user = get_jwt()
    roles = current_user.get("roles")
    if 'kurir' not in roles:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)
    # end_of_role_check
    pick_id = request.json.get("id", "")

    if not pick_id and not isinstance(pick_id, int):
        return Response(json.dumps({"message": "Missing order id."}),
                        status=400)
    try:
        if pick_id <= 0:
            return Response(json.dumps({"message": "Invalid order id."}),
                            status=400)
    except TypeError or ValueError:
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    existing_order = Order.query.filter_by(id=pick_id).first()

    if not existing_order or existing_order.status == "PENDING" or existing_order.status == "COMPLETE" :
        return Response(json.dumps({"message": "Invalid order id."}),
                        status=400)

    address = request.json.get("address", "")
    if not address:
        return Response(json.dumps({"message": "Missing address."}),
                        status=400)
    if len(address) < 42:
        return Response(json.dumps({"message": "Invalid address."}),
                        status=400)

    contract_address = existing_order.contract
    contract = web3.eth.contract(address=contract_address, abi=Configuration.CONTRACT_ABI)

    try:
        courier_acc = web3.eth.accounts[1]
        transaction = contract.functions.setCourier(courier_acc).transact({
            "from": web3.eth.accounts[0]
        })
        web3.eth.wait_for_transaction_receipt(transaction)
    except exceptions.ContractLogicError:
        return Response(json.dumps({"message": "Transfer not complete."}),
                        status=400)

    existing_order.status = "PENDING"
    database.session.commit()

    return Response(status=200)


@application.route("/", methods=["GET"])
def index():
    return f"Connected: {web3.is_connected()}"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port=5002, host="0.0.0.0")
    web3 = Web3(HTTPProvider("http://ganache-cli:8545"))