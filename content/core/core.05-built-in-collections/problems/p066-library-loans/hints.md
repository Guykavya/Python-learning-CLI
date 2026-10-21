## Hint 1

You need, per title, the available and total copies (two dicts, or a dict of two-item lists),
and per member, the set of titles they hold.

## Hint 2

`loans.setdefault(member, set())` gives the member's set. Checking "already has it" is
`title in loans[member]`.

## Hint 3

Check the four rules with `if`/`elif` in exactly the order given; the first failing rule decides
the message.
