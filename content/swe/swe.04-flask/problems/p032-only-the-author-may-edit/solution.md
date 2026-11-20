## Approach

```python
def get_post_for_edit(post_id):
    post = current_app.extensions["posts"].get(post_id)
    if post is None:
        abort(404)
    if g.user is None or post["author_id"] != g.user["id"]:
        abort(403)
    return post
```

Both `edit` and `delete` start with `post = get_post_for_edit(post_id)`; when the helper aborts, the rest of the view never runs, so nothing is changed.

Example: asha (id 1) posts to `/posts/2/edit`. The decorator lets her in (she is logged in), the helper finds post 2 with `author_id == 2`, `1 != 2`, so `abort(403)`. The title stays `Ravi's post`.

Why one helper? **Every** route that touches a post must make this check; with three copies, the fourth route (added next month) forgets it. This is the main source of real-world authorisation bugs. Hiding the *button* in the template is not a check: the attacker types the URL.

## Complexity

`O(1)` (dictionary lookup).

## Another way

Some apps answer **404** instead of 403 for other people's objects, so that the response does not even reveal that the object exists. Choose per resource; be consistent. Real projects also query with the owner in the `WHERE` clause (`WHERE id = :id AND author_id = :me`), so another user's row is simply not found.

## Not covered

Roles (admin may edit everything) and CSRF tokens on these POST routes (problem 17).
