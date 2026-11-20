## Hint 1

Picture the attacker: they have copied the database, and then also the server. For encrypted passwords, what do they now hold? For hashed passwords, what do they have to do to learn one password?

## Hint 2

Two different questions hide in "hash": *can it be reversed?* (no, by design) and *how fast can I try a guess?* (that is the cost). Answer them separately. Then for salt and pepper ask: where is it stored, and does it differ per user?

## Hint 3

```text
1. encrypt: key on the server -> all passwords read at once | hash: must guess each one
2. one-way: server cannot read or send a password after login
3. fast hash = billions of guesses/s | scrypt = slow + memory -> each guess is expensive
4. salt: random per password, stored with the hash | pepper: one secret, outside the DB, cost = hard to rotate
5. forgot password -> reset token, not recovery
```
