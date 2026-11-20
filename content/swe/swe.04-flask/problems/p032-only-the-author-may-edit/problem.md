# Only the author may edit

Chapter section 17. **Authentication** says who you are; **authorisation** says what you may do. The classic hole is an *insecure direct object reference*: the edit URL `/posts/2/edit` works for any logged-in user, because the view checks the login but not **whose post it is**.

In `solution.py` the starter has the login machinery (`login_required`, `g.user`) and the routes `POST /posts/<id>/edit` (form field `title`) and `POST /posts/<id>/delete`; both call the helper `get_post_for_edit(post_id)`. The posts are in `current_app.extensions["posts"]` (a dict id → post; each post has `author_id`). Write the helper so that the check lives in **one place**:

- the post does not exist → **404** (`abort(404)`),
- it exists but `g.user["id"]` is not its `author_id` → **403** (`abort(403)`),
- otherwise return the post.

Check the 404 first: a missing post is 404 for everybody. Both routes already call the helper (do not copy the check into them). Anonymous visitors are redirected to the login page by `login_required`.

## Example

```text
asha edits post 1 (hers)    -> 200 updated
asha edits post 2 (ravi's)  -> 403, the title is unchanged
asha deletes post 2         -> 403, the post still exists
asha edits post 99          -> 404
anonymous edits post 1      -> 302 to /auth/login?next=/posts/1/edit
```
