customer_response = """{
  "object": "customer",
  "id": "cust_test_5s1jz157366mu6wr0ng",
  "livemode": false,
  "location": "/customers/cust_test_5s1jz157366mu6wr0ng",
  "deleted": false,
  "metadata": {
  },
  "cards": {
    "object": "list",
    "data": [
      {
        "object": "card",
        "id": "card_test_5s1jzgw7oda499o8k0y",
        "livemode": false,
        "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards/card_test_5s1jzgw7oda499o8k0y",
        "deleted": false,
        "street1": null,
        "street2": null,
        "city": "Bangkok",
        "state": null,
        "phone_number": null,
        "postal_code": "10320",
        "country": "us",
        "financing": "credit",
        "bank": "JPMORGAN CHASE BANK N.A.",
        "brand": "Visa",
        "fingerprint": "7jGh9VWw5Dvm/8Zrh9wY/e3VXhdWyg8k8xD1+8sHGhU=",
        "first_digits": null,
        "last_digits": "4242",
        "name": "JOHN DOE",
        "expiration_month": 6,
        "expiration_year": 2024,
        "security_code_check": true,
        "tokenization_method": null,
        "created_at": "2022-06-05T09:38:32Z"
      },
      {
        "object": "card",
        "id": "card_test_5s1jzsw6iy9nw4gzmx3",
        "livemode": false,
        "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards/card_test_5s1jzsw6iy9nw4gzmx3",
        "deleted": false,
        "street1": null,
        "street2": null,
        "city": "Bangkok",
        "state": null,
        "phone_number": null,
        "postal_code": "10320",
        "country": "us",
        "financing": "credit",
        "bank": "JPMORGAN CHASE BANK N.A.",
        "brand": "Visa",
        "fingerprint": "7jGh9VWw5Dvm/8Zrh9wY/e3VXhdWyg8k8xD1+8sHGhU=",
        "first_digits": null,
        "last_digits": "4242",
        "name": "JOHN DOE",
        "expiration_month": 6,
        "expiration_year": 2024,
        "security_code_check": true,
        "tokenization_method": null,
        "created_at": "2022-06-05T09:39:29Z"
      }
    ],
    "limit": 20,
    "offset": 0,
    "total": 2,
    "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards",
    "order": "chronological",
    "from": "1970-01-01T00:00:00Z",
    "to": "2022-06-05T09:39:36Z"
  },
  "default_card": "card_test_5s1jzgw7oda499o8k0y",
  "description": "John Doe (id: 30)",
  "email": "john.doe@example.com",
  "created_at": "2022-06-05T09:37:17Z"
}"""


add_card_response = """{
  "object": "customer",
  "id": "cust_test_5s1jz157366mu6wr0ng",
  "livemode": false,
  "location": "/customers/cust_test_5s1jz157366mu6wr0ng",
  "deleted": false,
  "metadata": {
  },
  "cards": {
    "object": "list",
    "data": [
      {
        "object": "card",
        "id": "card_test_5s1jzgw7oda499o8k0y",
        "livemode": false,
        "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards/card_test_5s1jzgw7oda499o8k0y",
        "deleted": false,
        "street1": null,
        "street2": null,
        "city": "Bangkok",
        "state": null,
        "phone_number": null,
        "postal_code": "10320",
        "country": "us",
        "financing": "credit",
        "bank": "JPMORGAN CHASE BANK N.A.",
        "brand": "Visa",
        "fingerprint": "7jGh9VWw5Dvm/8Zrh9wY/e3VXhdWyg8k8xD1+8sHGhU=",
        "first_digits": null,
        "last_digits": "4242",
        "name": "JOHN DOE",
        "expiration_month": 6,
        "expiration_year": 2024,
        "security_code_check": true,
        "tokenization_method": null,
        "created_at": "2022-06-05T09:38:32Z"
      },
      {
        "object": "card",
        "id": "card_test_5s1jzsw6iy9nw4gzmx3",
        "livemode": false,
        "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards/card_test_5s1jzsw6iy9nw4gzmx3",
        "deleted": false,
        "street1": null,
        "street2": null,
        "city": "Bangkok",
        "state": null,
        "phone_number": null,
        "postal_code": "10320",
        "country": "us",
        "financing": "credit",
        "bank": "JPMORGAN CHASE BANK N.A.",
        "brand": "Visa",
        "fingerprint": "7jGh9VWw5Dvm/8Zrh9wY/e3VXhdWyg8k8xD1+8sHGhU=",
        "first_digits": null,
        "last_digits": "4242",
        "name": "JOHN DOE",
        "expiration_month": 6,
        "expiration_year": 2024,
        "security_code_check": true,
        "tokenization_method": null,
        "created_at": "2022-06-05T09:39:29Z"
      },
      {
        "object": "card",
        "id": "card_test_5s1k1g5nl9it6p44gda",
        "livemode": false,
        "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards/card_test_5s1k1g5nl9it6p44gda",
        "deleted": false,
        "street1": null,
        "street2": null,
        "city": "Bangkok",
        "state": null,
        "phone_number": null,
        "postal_code": "10320",
        "country": "us",
        "financing": "credit",
        "bank": "JPMORGAN CHASE BANK N.A.",
        "brand": "Visa",
        "fingerprint": "7jGh9VWw5Dvm/8Zrh9wY/e3VXhdWyg8k8xD1+8sHGhU=",
        "first_digits": null,
        "last_digits": "4242",
        "name": "JOHN DOE",
        "expiration_month": 6,
        "expiration_year": 2024,
        "security_code_check": true,
        "tokenization_method": null,
        "created_at": "2022-06-05T09:59:06Z"
      }
    ],
    "limit": 20,
    "offset": 0,
    "total": 3,
    "location": "/customers/cust_test_5s1jz157366mu6wr0ng/cards",
    "order": "chronological",
    "from": "1970-01-01T00:00:00Z",
    "to": "2022-06-05T09:59:14Z"
  },
  "default_card": "card_test_5s1jzgw7oda499o8k0y",
  "description": "John Doe (id: 30)",
  "email": "john.doe@example.com",
  "created_at": "2022-06-05T09:37:17Z"
}"""
