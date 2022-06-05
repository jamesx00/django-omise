customer_response = """{
    "object": "customer",
    "id": "cust_test_id",
    "livemode": false,
    "location": "/customers/cust_test_id",
    "deleted": false,
    "metadata": {
    },
    "cards": {
        "object": "list",
        "data": [
            {
                "object": "card",
                "id": "card_test_01",
                "livemode": false,
                "location": "/customers/cust_test_id/cards/card_test_01",
                "deleted": false,
                "street1": null,
                "street2": null,
                "city": null,
                "state": null,
                "phone_number": null,
                "postal_code": null,
                "country": "united states of america",
                "financing": "",
                "bank": "JPMORGAN CHASE BANK N.A.",
                "brand": "Visa",
                "fingerprint": "4ofhMPsiTp3xDz7AL9OO6kbo9vNDHiNmXnDmmdJSpLk=",
                "first_digits": null,
                "last_digits": "1111",
                "name": "john",
                "expiration_month": 10,
                "expiration_year": 2025,
                "security_code_check": true,
                "tokenization_method": null,
                "created_at": "2022-05-22T01:26:38Z"
                }
            ],
        "limit": 20,
        "offset": 0,
        "total": 1,
        "location": "/customers/cust_test_id/cards",
        "order": "chronological",
        "from": "1970-01-01T00:00:00Z",
        "to": "2022-06-05T05:41:28Z"
    },
    "default_card": "card_test_01",
    "description": null,
    "email": "johndoe@email.com",
    "created_at": "2022-05-22T01:26:20Z"
}"""
