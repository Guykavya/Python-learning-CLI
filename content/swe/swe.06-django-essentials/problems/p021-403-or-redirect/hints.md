## Hint 1

For every request ask two questions in order: is the user logged in? If yes, does the user have the permission? Which of the two questions makes Django answer with a redirect, and which with a 403?

## Hint 2

`PermissionRequiredMixin` and `@permission_required(..., raise_exception=True)` send an anonymous user to the login page but give a logged-in user without the permission a 403. Now look at `export`: its decorator has **no** `raise_exception`. What does the plain `@permission_required` do for a user who fails the check? Read section 13.4 again.

## Hint 3

```text
1  anonymous, LoginRequiredMixin           -> redirect to login, with ?next=/profile/
2  ann logged in, no view_user, raise=True -> 403
3  ann logged in, no view_user, no raise   -> redirect to login (the decorator treats "no permission" like "not logged in")
4  anonymous, PermissionRequiredMixin      -> redirect, ?next=/panel/
5  ann logged in, no change_user, mixin    -> 403
6  bob has change_user                     -> 200 panel
```
