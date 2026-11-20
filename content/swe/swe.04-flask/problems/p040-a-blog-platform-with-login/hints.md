## Hint 1

Work in the order of the chapter: 1) config and `before_request`, 2) the `csrf_token()` helper and the check, 3) `auth` (register, login, logout), 4) `blog` (index, show, new, edit, delete), 5) error handlers and the API. After each step run the tests: the first failing test names the next thing to build.

## Hint 2

Reuse what you wrote in the earlier problems: `validate_signup` (16), the CSRF check (17), `login_required` (30), the safe login (31), `get_post_for_edit` (32), pagination (25), the N+1 fix (26: `joinedload(Post.author)`), the rollback after `IntegrityError` (27), the error handlers (35). The tests check the HTML with CSS classes (`li.post`, `p.error`, `.nav-user`, `a.next`): keep those names.

## Hint 3

```text
create_app: config defaults -> test_config -> DictLoader -> csrf_token global -> db -> blueprints
before_request: g.user from session; for POST: compare_digest(form csrf_token, session csrf_token) else abort(400)
auth.register: validate; hash with HASH_METHOD; add; commit; except IntegrityError: rollback + error
auth.login: dummy hash for unknown user; session.clear(); session["user_id"]; redirect(safe_next)
blog.index: db.paginate(select(Post).options(joinedload(Post.author)).order_by(Post.id.desc()), page, PER_PAGE)
errors: errorhandler(HTTPException) and errorhandler(Exception): JSON under /api/, HTML page otherwise
```
