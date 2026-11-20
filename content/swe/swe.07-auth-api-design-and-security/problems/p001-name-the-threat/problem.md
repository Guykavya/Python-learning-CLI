# Name the threat

Chapter section 1.3 (a small threat model: STRIDE) and "Try it: name the threat". STRIDE is a checklist of six kinds of threat:

| Letter | Threat | Short test |
|---|---|---|
| `S` | Spoofing | someone **pretends to be** another user or system |
| `T` | Tampering | someone **changes** data, a token or a message that they should not change |
| `R` | Repudiation | someone can **deny** an action and nobody can prove otherwise |
| `I` | Information disclosure | someone **reads** what they should not |
| `D` | Denial of service | the service becomes **unusable** for others |
| `E` | Elevation of privilege | someone gets **more rights** than they were given |

Below are eight bugs in a small shop API. For each one, give the **one** STRIDE letter that names the **main** threat, as the first thing the attacker achieves. No program is shown; this is a reading exercise.

1. A hidden form field says `price=1500`. The attacker edits it to `price=1`, and the server saves the order with that price.
2. A normal customer sends `PATCH /users/7` with `{"role": "admin"}`. The server stores the new role, and from then on the account can open the admin pages.
3. An attacker finds Asha's password in an old leak and logs in as Asha.
4. A crash page shows the full SQL query, the file path of the server and the database password.
5. A script sends 20,000 search requests per second from one address, and the server stops answering real customers.
6. A support agent refunds an order. The system keeps no audit log. Later the agent says "I never did that", and nobody can prove it.
7. On a café Wi-Fi, a stranger changes the amount inside a JSON response while it travels from a server on plain HTTP to the app. The app then shows the wrong total.
8. `GET /orders/2`, sent by user 1, returns the full order of user 2 (name, address, items).

## Answer format

Write exactly eight lines, one per bug, in this form (the bug number, a colon, a space, one capital letter from `S T R I D E`):

```text
1: X
2: X
...
8: X
```

## After you answer

- Which two letters appear twice in the model answer, and what do the two bugs have in common?
- Bug 3 also lets the attacker read Asha's orders afterwards. Why is the main threat still the letter you chose?
- For bug 2, which chapter 1.4 question was forgotten?
