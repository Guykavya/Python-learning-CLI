# What does a framework remove?

Chapter section 1.1. In swe.02 you wrote an HTTP server from raw sockets: read bytes until the blank line, split the request line and the headers, look at `Content-Length`, build a response with a status line and a correct `Content-Length`, and deal with broken input yourself. A Flask app does the same job in a few decorators.

In `answer.md` (about 200 words) compare the two on **five** points. For each, say *what you wrote by hand in the socket server* and *what Flask does for you*:

1. **Routing** (choosing the code for a URL and method)
2. **Parsing the request** (query string, form, JSON, cookies, files)
3. **Building the response** (status line, headers, `Content-Length`, content type)
4. **Errors** (a path that does not exist, a method that is not allowed, a crash in your code)
5. **Testing** (how do you exercise the code without starting a server?)

Then add **one sentence** on what the framework does **not** remove: name at least two things that are still your job.
