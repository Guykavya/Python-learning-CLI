- Only handling lower→upper. `HTTPServer` then becomes `httpserver`: there is no small letter
  before the `S`.
- Splitting before **every** capital: `HTTPServer` becomes `h_t_t_p_server`.
- Using `"\1_\2"` without `r`. The replacement then contains control characters.
- Trying `to_camel` with a replacement string like `r"\1".upper()`. That upper-cases the
  string `"\1"` (no letters to change) before `re.sub` ever runs. Use a function.
- Writing `_([a-z])` without the lookbehind: `_private_var` becomes `PrivateVar`.
- Using `[a-z]` after the `_` only. Then `utf_8` keeps its underscore.
