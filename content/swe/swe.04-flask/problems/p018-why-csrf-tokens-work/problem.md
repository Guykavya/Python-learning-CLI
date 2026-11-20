# Why CSRF tokens work

Chapter sections 9.2, 9.3 and 16.5. A bank site, `bank.example`, uses a session cookie for login. You are logged in. In another tab you open `evil.example`, whose page contains a hidden form that **posts automatically** to `https://bank.example/transfer` with `to=attacker&amount=500`.

In `answer.md` write a clear explanation (about 150 to 250 words) that answers:

1. **What does the browser do** with your bank cookie when `evil.example` sends that POST? Does the attacker's page see the cookie or the response?
2. **Why does a CSRF token in the bank's form stop the attack?** Say what the attacker's page can and cannot know, and name the browser rule that makes the difference (the **same-origin policy**).
3. **What does `SameSite=Lax` change?** Name one thing it blocks and one situation where it is **not** enough on its own.
4. Why must `GET /transfer?to=...&amount=...` never change data?

A good answer uses the words *cookie*, *token*, *origin*, *forged request*.
