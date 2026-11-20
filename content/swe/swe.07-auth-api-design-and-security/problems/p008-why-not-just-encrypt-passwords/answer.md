## Model answer

**Encryption is reversible.** Encrypted passwords can be turned back into the originals by anyone who has the **key**. The key has to be available to the running application, so a thief who gets the server (or a backup plus the config) gets the key and reads **every** password at once. Many people reuse one password on other sites, so the damage leaves your system.

**Hashing is one-way.** After login the server knows nothing about the password except whether a string matches the stored hash. It cannot read it, send it or leak it, and neither can a stolen copy of the database. Being unable to e-mail the password is therefore a feature. (Sending a password by e-mail is a bad idea anyway.)

**Slow hash, not a fast one.** SHA-256 is built to be fast: a GPU tries billions of guesses per second, so a **brute force** attack on a stolen table of fast hashes finishes quickly. scrypt (also Argon2id, bcrypt) is deliberately slow and needs a lot of memory, so each guess costs the attacker as much as it costs you once per login. The cost is stored in the hash string, so you can raise it later.

**Salt and pepper.** A **salt** is a random value, different for every password, stored next to the hash. It makes equal passwords give different hashes and makes precomputed tables useless. A **pepper** is one secret for the whole system, kept **outside** the database (environment, secrets manager) and mixed in before hashing; a thief with only the database still needs it. The cost: you cannot lose or rotate it casually, because every hash depends on it, so keep a version number.

**Forgotten passwords.** Never "recover" the password. Send a **reset token**: random, stored only as a hash, short-lived, single use (chapter 2.6). The user then chooses a new password.

**Checklist: your answer should mention**
- [ ] encryption is reversible, and whoever gets the key (on the server) reads all passwords
- [ ] a hash is one-way: the server never knows the password after login, so it cannot leak or e-mail it
- [ ] fast hashes (SHA-256) allow billions of guesses per second; a slow, memory-hard hash (scrypt, Argon2id, bcrypt) makes brute force expensive
- [ ] the cost is stored in the hash string, so it can be raised later
- [ ] the salt: random per password, stored with the hash, defeats precomputed tables and equal hashes
- [ ] the pepper: a secret outside the database; extra protection, but hard to rotate (needs a version number)
- [ ] forgotten password: a reset token (random, hashed in storage, short-lived, single use), never recovery
