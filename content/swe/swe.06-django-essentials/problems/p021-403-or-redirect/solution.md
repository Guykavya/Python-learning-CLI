## Approach

Trace each request through two checks: **authentication** (who are you?) and **authorisation** (may you?).

```text
1: 302 /accounts/login/?next=/profile/
2: 403
3: 302 /accounts/login/?next=/export/
4: 302 /accounts/login/?next=/panel/
5: 403
6: 200 panel
```

- **1.** `LoginRequiredMixin` and an anonymous user: redirect to `LOGIN_URL` with the asked path in `next`.
- **2.** `ann` is logged in but has no `view_user`. With `raise_exception=True` the decorator raises `PermissionDenied`, which becomes **403**.
- **3.** Same user, same missing permission, but the decorator has no `raise_exception`. Then `permission_required` redirects to the login page even though `ann` is already logged in. This is the trap of the exercise.
- **4.** `PermissionRequiredMixin` with an anonymous user: a redirect (the mixin's `handle_no_permission` checks `raise_exception` and whether the user is authenticated).
- **5.** The same mixin with a logged-in user who lacks `change_user`: **403**.
- **6.** `bob` has the permission: 200.

Real output of the program, run with Django 6.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Remember it as a rule: *not logged in -> redirect; logged in but not allowed -> 403*. The decorator `@permission_required` without `raise_exception=True` is the one exception, because it was written to redirect in both cases. In a browser a 403 is the better answer for a logged-in user, so write `raise_exception=True` (or use the mixin) for permission checks.
