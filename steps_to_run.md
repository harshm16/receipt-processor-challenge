# Steps to Run

## Requirements
- Docker
- Clone repo:
        git clone git@github.com:harshm16/receipt-processor-challenge.git


## Steps

- CD into the repo directory
- Build the image 
   
        docker build -t receipt-processor .
   
- Run the webservice server

        docker run -p 5000:5000 receipt-processor
   
- Send POST and GET requests to `http://127.0.0.1:5000`

## Examples

- To process a receipt

            curl --header "Content-Type: application/json" \
            --request POST \
            --data '{"retailer": "Target", "purchaseDate": "2022-01-02", "purchaseTime": "13:13", "total": "1.25", "items": [{ "shortDescription": "Pepsi - 12-oz", "price": "1.25" }]}' \
            http://localhost:5000/receipts/process

        Example response:

            { "id": "7fb1377b-b223-49d9-a31a-5a02701dd310" }

- To Get receipt points for the above receipt (add the generated receipt_id in place of < id > below):

            curl --request GET http://localhost:5000/receipts/< id >/points

        Example response:

            {"points":31}


## Finding/Bug:

- The second example ("retailer": "M&M Corner Market") in the README doesn't get processed because of the defined patter for 'retailer' in api.yml file.

    - The pattern doesn't allow characters with whitespace.