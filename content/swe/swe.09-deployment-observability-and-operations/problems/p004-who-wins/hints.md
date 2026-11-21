## Hint 1

Take one setting at a time and write the five layers as a column, weakest to strongest. Cross out the layers that do not mention the setting. The last one left standing wins, **after** you have worked out what `${...}` in the `environment:` layer expands to.

## Hint 2

For a `${NAME:-fallback}` in `environment:`, ask three questions in order: is `NAME` set in the **shell**? If not, is it in the **`.env` file**? If not, use the fallback. `PORT` and `LOG_LEVEL` take different paths. For `REDIS_URL` only the text `${REDIS_HOST:-redis}` is replaced, not the whole value.
