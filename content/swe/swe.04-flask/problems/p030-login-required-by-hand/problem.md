# `login_required`, by hand

Chapter sections 16.3 and 16.4. In `solution.py` the starter has a tiny user table `USERS` (ids 1 and 2), the factory, and the routes `/`, `/auth/login`, `/dashboard`, `/settings` and `/posts/<int:post_id>/private`. Write:

- A `before_request` hook `load_user` that sets **`g.user`** to the user dict for `session["user_id"]`, or to `None` when nobody is logged in (an unknown id counts as nobody).
- The decorator **`login_required(view)`**: when `g.user` is `None`, redirect (**302**) to the login page with the page the visitor wanted in a `next` parameter: `/auth/login?next=/dashboard` (build it with `url_for("login", next=request.path)`). Otherwise run the view with all its arguments.
- It must use **`functools.wraps`**, so the decorated functions keep their names. (Without it all protected views are called `wrapper`, and registering the second one fails with *"View function mapping is overwriting an existing endpoint function"*.)
- The decorator goes **under** `@app.get(...)`: the route must register the protected function.

The home page `/` and the login page stay public.

## Example

```text
GET /dashboard (anonymous)         -> 302 Location: /auth/login?next=/dashboard
GET /dashboard (user_id 1 in the session) -> 200 Dashboard of asha
GET /posts/5/private (anonymous)   -> 302 .../auth/login?next=/posts/5/private
```
