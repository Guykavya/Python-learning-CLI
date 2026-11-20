## Hint 1

Where exactly is the list of background tasks kept? What happens to that place when `uvicorn` is restarted during a deploy, at second 20 of the 40-second PDF?

## Hint 2

For the payload question, imagine the customer cancels the order 10 seconds after placing it, and the receipt job runs 30 seconds later. What does a job holding the whole object send, and what does a job holding only `order_id` (and reading the order when it runs) send?
