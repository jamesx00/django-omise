base_schedule_response = """
{
  "object": "schedule",
  "id": "test_schedule_id",
  "deleted": false,
  "livemode": false,
  "location": "/schedules/test_schedule_id",
  "every": 1,
  "occurrences": {
    "object": "list",
    "data": [
      {
        "object": "occurrence",
        "livemode": false,
        "location": "/occurrences/test_occurrence_id",
        "id": "test_occurrence_id",
        "result": "chrg_test_5s63wg5cfhlc63ww0os",
        "schedule": "test_schedule_id",
        "message": null,
        "status": "successful",
        "processed_at": "2022-06-17T01:01:47Z",
        "created_at": "2022-06-17T01:01:47Z",
        "scheduled_on": "2022-06-17",
        "retry_on": null
      }
    ],
    "limit": 20,
    "offset": 0,
    "total": 1,
    "location": "/schedules/test_schedule_id/occurrences",
    "order": "chronological",
    "from": "1970-01-01T00:00:00Z",
    "to": "2022-06-17T01:02:04Z"
  },
  "on": {
    "days_of_month": [
      17
    ]
  },
  "in_words": "Every 1 month(s) on the 17th",
  "period": "month",
  "status": "running",
  "active": true,
  "charge": {
    "object": "scheduled_charge",
    "id": "test_schedule_charge_id",
    "livemode": false,
    "currency": "THB",
    "amount": 200000,
    "default_card": true,
    "card": "test_card_id",
    "customer": "test_customer_id",
    "description": "test charge",
    "metadata": {
    },
    "created_at": "2022-06-17T01:01:47Z"
  },
  "next_occurrences_on": [
    "2022-07-17",
    "2022-08-17",
    "2022-09-17",
    "2022-10-17",
    "2022-11-17",
    "2022-12-17",
    "2023-01-17",
    "2023-02-17",
    "2023-03-17",
    "2023-04-17",
    "2023-05-17",
    "2023-06-17"
  ],
  "ended_at": null,
  "start_on": "2022-06-17",
  "end_on": "2023-06-17",
  "created_at": "2022-06-17T01:01:47Z"
}"""

schedule_response_no_next_occurrences_on = """
{
  "object": "schedule",
  "id": "test_schedule_id",
  "deleted": false,
  "livemode": false,
  "location": "/schedules/test_schedule_id",
  "every": 1,
  "occurrences": {
    "object": "list",
    "data": [
      {
        "object": "occurrence",
        "livemode": false,
        "location": "/occurrences/test_occurrence_id",
        "id": "test_occurrence_id",
        "result": "chrg_test_5s63wg5cfhlc63ww0os",
        "schedule": "test_schedule_id",
        "message": null,
        "status": "successful",
        "processed_at": "2022-06-17T01:01:47Z",
        "created_at": "2022-06-17T01:01:47Z",
        "scheduled_on": "2022-06-17",
        "retry_on": null
      }
    ],
    "limit": 20,
    "offset": 0,
    "total": 1,
    "location": "/schedules/test_schedule_id/occurrences",
    "order": "chronological",
    "from": "1970-01-01T00:00:00Z",
    "to": "2022-06-17T01:02:04Z"
  },
  "on": {
    "days_of_month": [
      17
    ]
  },
  "in_words": "Every 1 month(s) on the 17th",
  "period": "month",
  "status": "running",
  "active": true,
  "charge": {
    "object": "scheduled_charge",
    "id": "test_schedule_charge_id",
    "livemode": false,
    "currency": "THB",
    "amount": 200000,
    "default_card": true,
    "card": "test_card_id",
    "customer": "test_customer_id",
    "description": "test charge",
    "metadata": {
    },
    "created_at": "2022-06-17T01:01:47Z"
  },
  "ended_at": null,
  "start_on": "2022-06-17",
  "end_on": "2023-06-17",
  "created_at": "2022-06-17T01:01:47Z"
}"""
