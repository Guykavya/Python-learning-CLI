# Why not just encrypt passwords?

Chapter sections 2.1 to 2.3 and "Try it: why not just encrypt passwords?". A teammate says: "Let us encrypt the passwords with AES instead of hashing them. Then we can e-mail users their password when they forget it." You must explain why this is the wrong plan, and what to do instead.

In `answer.md` write a clear explanation (about 150 to 300 words) that covers:

1. **Encryption versus hashing:** what happens if an attacker steals the database **and** the application server (where the key must live)?
2. **Why a hash is one-way** and why that is a feature: what does the server know about a password after login?
3. **Slow hash versus fast hash:** why is SHA-256 alone a poor choice for passwords, and why is a slow, memory-hungry hash such as scrypt a good one?
4. **Salt versus pepper:** what does each one protect against, where does each one live, and what is the cost of a pepper?
5. **What to do** when a user forgets a password.

A good answer uses the words *reversible*, *key*, *one-way*, *brute force*, *salt*, *pepper*, *reset token*.

## After you answer

Compare with `answer.md` and tick the checklist. In the module of problem p003, find which part of the stored string is the salt and which the cost.
