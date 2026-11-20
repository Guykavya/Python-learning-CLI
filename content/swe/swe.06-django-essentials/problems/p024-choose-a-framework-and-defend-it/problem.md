# Choose a framework and defend it

Chapter section 19 (the five questions in 19.2, the defence in 19.4). This is the outcome of the whole module: **choose a framework for a job and defend the choice.** There is no best framework, only a best fit.

Below are three jobs. Everyone answers the same three, so you can compare your answer with the model answer.

- **B.** A public JSON API for a mobile app. About 500 clients at the same time. Each request calls an ML model service over the network and returns its answer. No web pages, no admin.
- **D.** A content site: visitors register and log in, write comments, moderators approve or delete them, pages must be good for search engines, and editors need a screen to write articles.
- **G.** A working Django online shop must show customers live notifications when their order status changes. (The shop has 30,000 lines of tested code.)

In `answer.md` write about **200 to 350 words in total** (roughly 70 to 120 words per job). For **each** job choose Django, Flask or FastAPI (a combination is allowed) and give the four parts of a defence:

1. the **choice** and the reasons, tied to the job (use the five questions of section 19.2: who is the user, how central is the data model, is the work mostly waiting, how much do you want to decide yourself, how long will the project live);
2. the **cost** you accept;
3. the **trigger** that would make you change your mind.

Do not write "it is faster" or "everyone uses it" without a reason: those are weak defences.

## Example (a different job)

Job: "a 30-line endpoint that receives a payment webhook." Choice: Flask, because one endpoint needs no admin, ORM or templates and the real work is checking the signature. Cost: nothing noticeable. Trigger: if more endpoints and validation appear, move to FastAPI.

## Checking yourself

When you have written your answer, open `answer.md`, read the model answer, and tick the checklist honestly. An answer without a cost and a trigger for each job is not finished.
