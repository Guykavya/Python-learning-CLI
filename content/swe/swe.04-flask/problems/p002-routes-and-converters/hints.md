## Hint 1

What does Flask pass to the view for `/post/<post_id>` when the URL is `/post/abc`? And is that what you want for something called an *id*?

## Hint 2

A converter goes before the name: `<int:post_id>`, `<path:subpath>`. A rule with `int` simply does not match `/post/abc`, so Flask answers 404 on its own.

## Hint 3

```text
@app.route("/user/<username>")            -> user_profile
@app.route("/post/<int:post_id>")          -> show_post
@app.route("/files/<path:subpath>")        -> show_file
```
