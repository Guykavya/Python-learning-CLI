## Approach

Ask one question per bug and pick the letter that answers it (chapter 1.3).

```text
1: T
2: E
3: S
4: I
5: D
6: R
7: T
8: I
```

- **1: T.** The attacker changed data the server should have computed itself (the price). Defence: never trust a price from the client, read it from the database (chapters 1.2 and 14).
- **2: E.** The thing that was changed is the **role**, so the attacker gains rights they were not given. This is "mass assignment": the endpoint accepted a field it should have ignored. Defence: an allow-list of fields the user may change (chapter 8.5).
- **3: S.** The attacker pretends to be Asha with her password. What they read afterwards is a result, not the first thing they achieved. Defence: multi-factor authentication, rate limits (chapters 2 and 6).
- **4: I.** An error page that prints secrets discloses information. Defence: generic errors for users, details only in the log (chapter 15.7).
- **5: D.** One client makes the service unusable for the others. Defence: rate limits (chapter 11).
- **6: R.** Repudiation: nobody can prove who acted. Defence: an append-only audit log with who, what, when (chapter 15.6).
- **7: T.** Data was changed in transit. Defence: HTTPS, and signatures where it matters (chapters 1.5 and 4).
- **8: I.** User 1 reads user 2's order: a missing ownership check (IDOR). No fake identity is used. Defence: scope the query to the owner (chapter 8).

The two letters that appear twice are `T` (bugs 1 and 7: data changed, once at the client and once on the wire) and `I` (bugs 4 and 8: information read that should not be read, once by accident in an error page and once through a missing check).

How the answer was produced: this is a judgement exercise, so there is no program output; the model answer follows the definitions in chapter 1.3.

## Complexity

Not applicable.

## Another way

Many bugs fit more than one letter (the chapter says so). The method that never fails is to go through STRIDE for **each part of the system** and ask all six questions, instead of labelling a bug after the fact.
