# Fix the login view

Chapter sections 16.3 and 16.6. The login view in `starter.py` works, and it has **three security bugs**. Fix them in `solution.py` without changing what a normal login does.

1. **User enumeration.** It answers `No such user` for an unknown name and `Wrong password` for a bad password, so an attacker can find out which names exist. Both cases must give the **same status (401) and the same body** (`Invalid username or password`). They must also cost the **same work**: for an unknown user still check the password against a dummy hash (`DUMMY_HASH`, given in the starter) so that the response time does not reveal the name either. (The tests count the calls of `check_password_hash`: exactly one per attempt.)
2. **Session fixation.** After a successful login it just adds `session["user"]`, keeping whatever the old session held. Call **`session.clear()`** first, then set the user.
3. **Open redirect.** After login it redirects to `request.args["next"]` whatever it is, so a link like `/auth/login?next=https://evil.example/` sends a freshly logged-in user to an attacker's site. Only redirect to a **local path**: it must start with a single `/`, must have **no scheme or host** (`https://x`, `//x`, `javascript:...`) and **no backslash** (`/\evil.example` is read as `//evil.example` by browsers). Anything else goes to `/`.

A normal login (`POST /auth/login?next=/dashboard` with the right password) still answers **302** to `/dashboard` (or `/` without `next`) and `GET /` then says `Hello asha`.

## Example

```text
POST /auth/login username=nobody password=x   -> 401 Invalid username or password
POST /auth/login username=asha  password=bad  -> 401 Invalid username or password
POST /auth/login?next=https://evil.example/   (right password) -> 302 Location: /
POST /auth/login?next=/dashboard?tab=2         (right password) -> 302 Location: /dashboard?tab=2
```
