## Approach

The point of the exercise is to see a framework as **a set of chores you no longer write**, and to see that the chores are the ones that are tedious and easy to get wrong, not the interesting decisions.

See `answer.md` for the model answer and the checklist.

Example: the raw server needed about 15 lines only to find out *where the body ends* (`Content-Length`). In Flask that line is gone, and so is the class of bugs where a missing or wrong length makes a client hang.

## Complexity

Not applicable.

## Another way

Think of the layers as a stack: the **server** (Gunicorn) speaks HTTP and sockets; **WSGI** is the plug between the server and your app; **Flask/Werkzeug** turn `environ` into `request` and a return value into a response; **your code** decides what the page does.

## Not covered

What a framework *costs*: a dependency to update, magic (contexts, proxies) to learn, and one more place for bugs. The raw version is worth writing once, as you did.
