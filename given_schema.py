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