schedule_with_one_charge_event_response = """
{
  "object": "event",
  "id": "test_event_id",
  "livemode": false,
  "location": "/events/test_event_id",
  "webhook_deliveries": [],
  "data": {
    "object": "schedule",
    "id": "test_schedule_id",
    "deleted": false,
    "livemode": false,
    "location": "/schedules/test_schedule_id",
    "every": 1,
    "occurrences": {
      "object": "list",
      "data": [],
      "limit": 20,
      "offset": 0,
      "total": 0,
      "location": "/schedules/test_schedule_id/occurrences",
      "order": "chronological",
      "from": "1970-01-01T07:00:00+07:00",
      "to": "2022-06-17T08:40:54+07:00"
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
      "amount": 100000,
      "default_card": false,
      "card": "test_card_id",
      "customer": "test_customer_id",
      "description": "",
      "metadata": {},
      "created_at": "2022-06-17T08:40:54+07:00"
    },
    "next_occurrences_on": [
      "2022-06-17",
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
    "created_at": "2022-06-17T08:40:54+07:00"
  },
  "key": "schedule.create",
  "created_at": "2022-06-17T01:40:54Z"
}"""
