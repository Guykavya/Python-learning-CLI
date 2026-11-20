## Model answer

**1. Routing.** By hand: an `if`/`elif` chain on `(method, path)`, with string splitting to pull out ids. Flask: `@app.route("/post/<int:post_id>", methods=[...])` maps patterns to functions, converts and validates the parts of the URL, and builds URLs back with `url_for`.

**2. Parsing the request.** By hand: read bytes until `\r\n\r\n`, split lines, build a headers dict, read exactly `Content-Length` bytes, decode the query string and the form, parse JSON, parse `Cookie`. Flask gives a `request` object with `args`, `form`, `files`, `get_json()`, `headers` and `cookies`, already decoded.

**3. Building the response.** By hand: write the status line and each header, compute `Content-Length` in bytes, encode the body. Flask turns a returned string, dict (JSON) or tuple `(body, status, headers)` into a correct response and sets the content type and length.

**4. Errors.** By hand: you answered 404/405/500 yourself and had to make sure a crash did not kill the server loop. Flask answers 404 and 405 (with `Allow`) from the router, turns an uncaught exception into a 500 and lets you register handlers for each code or exception class.

**5. Testing.** By hand: start the server on a port in a thread and connect a socket. Flask has a WSGI interface, so `app.test_client()` calls the app as a function: no port, no network, milliseconds per test.

**What it does not remove.** The framework does not decide *what is allowed*: input validation, authentication and authorisation, CSRF protection, and the design of your data and database remain your job (Flask gives you the places to plug them in, not the rules).

**Checklist: your answer should mention**
- [ ] routing: patterns, converters and `url_for` instead of `if` chains
- [ ] request parsing: `request.args`/`form`/`get_json()` instead of splitting bytes by hand
- [ ] response building: returning a value instead of writing status line, headers and `Content-Length`
- [ ] errors: 404/405 and 500 handled by the framework (plus error handlers)
- [ ] testing: `test_client()` without a server
- [ ] still your job: validation, authentication/authorisation, security rules, data design
