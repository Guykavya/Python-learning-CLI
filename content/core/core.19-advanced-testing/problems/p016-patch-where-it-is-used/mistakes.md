- Patching where the object is **defined** (`clock.now`) for a `from clock import now` module. The
  test passes the patch silently and the real function runs.
- Patching `os.path.exists` globally for `has_config`: it works here, but it also changes the answer
  for every other piece of code (including pytest) while the patch is active. Patch the narrow name.
- Writing `"mailer.Mailer"` for `welcome`: the `Mailer` that `app_mail` calls is its own reference.
- Forgetting that a patched class returns `target.return_value` when called: configure
  `mock.return_value.send.return_value`, not `mock.send.return_value`.
