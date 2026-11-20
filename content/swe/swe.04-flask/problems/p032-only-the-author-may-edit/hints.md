## Hint 1

Which two questions does the helper answer? "Does it exist?" and "Is it yours?" In which order should they be asked, and which HTTP status goes with each?

## Hint 2

`abort(404)` and `abort(403)` raise an HTTP exception and end the view. `g.user` is a dict (or `None`) filled in by the `before_request` hook: compare `g.user["id"]` with `post["author_id"]`. Do not repeat the check in the routes: they already call the helper.

## Hint 3

```text
def get_post_for_edit(post_id):
    post = posts.get(post_id)
    if post is None: abort(404)
    if g.user is None or post["author_id"] != g.user["id"]: abort(403)
    return post
```
