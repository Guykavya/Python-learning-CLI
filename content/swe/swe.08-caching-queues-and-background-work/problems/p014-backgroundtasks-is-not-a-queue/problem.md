# `BackgroundTasks` is not a queue

Chapter sections 8.2 (what belongs in a job) and 8.3 (`BackgroundTasks` is not a queue). A teammate wrote this FastAPI endpoint (swe.05 section 14):

```python
@app.post("/orders", status_code=201)
def create_order(order: OrderIn, background: BackgroundTasks, db=Depends(get_db)):
    saved = save_order(db, order)
    background.add_task(send_receipt_email, saved)           # the whole Order object
    background.add_task(generate_invoice_pdf, saved)          # takes about 40 seconds
    return {"id": saved.id}
```

They say: "Background tasks run after the response, so this is the same as a job queue, and simpler."

In `answer.md` explain (about 150 to 250 words):

1. Three things that are **lost or go wrong** with `BackgroundTasks` when the server is restarted for a deploy, crashes, or is busy. Use the 40-second PDF as one example.
2. What a **durable queue** adds. Name at least four properties.
3. What should be in the job **payload**, and why not the whole `Order` object. Give two reasons.
4. When `BackgroundTasks` **is** a reasonable choice. Give one example.
5. What the endpoint could return instead of making the client wait for the PDF (status code and body).

Use the words *process*, *durable*, *retry*, *payload*, *id*.

## Example

A good sentence for part 1: "The tasks live only in the memory of the web process, so ..."
