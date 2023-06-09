from flask import Flask, jsonify, request
import uuid
import jsonschema
import os
from math import ceil
from datetime import datetime


app = Flask(__name__)

#stores all the user entered receipts
receipts = {}

# JSON Schema for validating the receipt - as provided in api.yml
receipt_schema = {
    "type": "object",
    "required": ["retailer", "purchaseDate", "purchaseTime", "items", "total"],
    "properties": {
        "retailer": {
            "description": "The name of the retailer or store the receipt is from.",
            "type": "string",
            "pattern": "^\\S+$"
        },
        "purchaseDate": {
            "description": "The date of the purchase printed on the receipt.",
            "type": "string",
            "format": "date"
        },
        "purchaseTime": {
            "description": "The time of the purchase printed on the receipt. 24-hour time expected.",
            "type": "string",
            "format": "time"
        },
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/definitions/item"}
        },
        "total": {
            "description": "The total amount paid on the receipt.",
            "type": "string",
            "pattern": "^\\d+\\.\\d{2}$"
        }
    },
    "definitions": {
        "item": {
            "type": "object",
            "required": ["shortDescription", "price"],
            "properties": {
                "shortDescription": {
                    "description": "The Short Product Description for the item.",
                    "type": "string",
                    "pattern": "^[\\w\\s\\-]+$"
                },
                "price": {
                    "description": "The total price paid for this item.",
                    "type": "string",
                    "pattern": "^\\d+\\.\\d{2}$"
                }
            }
        }
    }
}

#function to calculate points based on given conditions
def calculate_points(receipt):
    points = 0

    # One point for every alphanumeric character in the retailer name.
    retailer_points = sum(c.isalnum() for c in receipt['retailer'])
    points += retailer_points

    # 50 points if the total is a round dollar amount with no cents.
    total = float(receipt['total'])
    if total.is_integer():
        points += 50

    # 25 points if the total is a multiple of 0.25.
    if total % 0.25 == 0:
        points += 25

    # 5 points for every two items on the receipt.
    item_count = len(receipt['items'])
    points += item_count // 2 * 5

    # If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 
    # and round up to the nearest integer. The result is the number of points earned.
    for item in receipt['items']:
        description_length = len(item['shortDescription'].strip())
        if description_length % 3 == 0:
            price = float(item['price'])
            points += ceil(price * 0.2)

    # 6 points if the day in the purchase date is odd.
    purchase_date = int(datetime.strptime(receipt['purchaseDate'], "%Y-%m-%d").day)
    if purchase_date % 2 == 1:
        points += 6

    # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    two_pm = datetime.strptime("14:00", "%H:%M")
    four_pm = datetime.strptime("16:00", "%H:%M")

    purchase_time = datetime.strptime(receipt['purchaseTime'], "%H:%M")
    if two_pm < purchase_time < four_pm:
        points += 10

    return points

# Post method
@app.route('/receipts/process', methods=['POST'])
def create_receipt():
    receipt_data = request.json

    # Validating the received JSON data against the schema
    try:
        jsonschema.validate(receipt_data, receipt_schema)
    except jsonschema.exceptions.ValidationError as e:
        return jsonify({'The receipt is invalid': e.message}), 400

    # Generating a unique receipt ID 
    receipt_id = str(uuid.uuid4())
    receipt_data['id'] = receipt_id

    #calculating the score and then adding the receipt to the our receipts store (dictionary)
    receipt_data['points'] = calculate_points(receipt_data)
    receipts[receipt_id] = receipt_data

    # Return the receipt ID as a JSON response
    response = {'id': receipt_id}
    return jsonify(response), 200

# Get method
@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_receipt(receipt_id):
    if receipt_id in receipts:
        return jsonify({'points': receipts[receipt_id]['points']})
    else:
        return jsonify({'error': 'No receipt found for that id'}), 404


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
