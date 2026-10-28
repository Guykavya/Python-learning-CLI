## Hint 1

There are two different operations: **attach** a zone to a naive time (`replace(tzinfo=...)`, the clock reading stays the same) and **convert** an aware time to another zone (`astimezone(...)`, the instant stays the same). `to_utc` needs one of each, in which order?

## Hint 2

Check the inputs first with your own `is_aware`: raise `ValueError` for the wrong kind. For `same_instant`, two aware datetimes compare with `==` by instant, even across different zones. What does `==` return for an aware and a naive datetime? (It quietly returns `False`; that is why you must check first.)

## Hint 3

```
is_aware(dt):      return dt.tzinfo is not None and dt.utcoffset() is not None

to_utc(naive, zone):
    if is_aware(naive): raise ValueError
    return naive.replace(tzinfo=ZoneInfo(zone)).astimezone(timezone.utc)

utc_to_local(moment, zone):
    if not is_aware(moment): raise ValueError
    return moment.astimezone(ZoneInfo(zone))

same_instant(a, b):
    if not (is_aware(a) and is_aware(b)): raise ValueError
    return a == b
```
