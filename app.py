from flask import Flask, jsonify, request
import uuid
import jsonschema
import os
from math import ceil
from datetime import datetime
from given_schema import receipt_schema

app = Flask(__name__)

#stores all the user entered receipts
receipts = {}

def calculate_points(receipt):
    """
    calculate_points(receipt)
    
    for a given json representing the entered receipt, it calculates points based on given conditions
    
    Parameters
    -----------
    
    receipt (dict): Receipt json
    
    Returns
    -----------
    
    points (int): Points based on conditions
    
    """ 

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


@app.route('/receipts/process', methods=['POST'])
def create_receipt():
    """
    create_receipt()

    Post method which stores the given receipt alongwith its points.

    Parameters
    -----------

    Returns
    -----------

     (str): Response: 400 response if receipt invalid, if valid - 200 response with generated id.

    """ 

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



@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_receipt(receipt_id):
    """
    get_receipt(receipt_id)
    
    GET method which returns the points for a given receipt id.
    
    Parameters
    -----------
    
    receipt_id (str): Generated receipt id
    
    Returns
    -----------
    
     (str): points: 'points' / error: 404
    
    """ 
    if receipt_id in receipts:
        return jsonify({'points': receipts[receipt_id]['points']})
    else:
        return jsonify({'error': 'No receipt found for that id'}), 404


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
