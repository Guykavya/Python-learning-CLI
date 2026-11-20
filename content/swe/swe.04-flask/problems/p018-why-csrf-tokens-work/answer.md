## Model answer

**1. The browser's behaviour.** Browsers attach the cookies of `bank.example` to **every** request sent to `bank.example`, no matter which page caused the request. So the forged POST arrives with your valid session cookie, and the bank sees "a logged-in user asking for a transfer". The attacker's page cannot read the cookie (it belongs to another origin) and cannot read the response, but it does not need to: it only needs the **side effect**.

**2. Why the token stops it.** A CSRF token is a second secret, tied to the session, that the **page** must put into the request (a hidden field or a header). The cookie is sent automatically by the browser; the token is not. To forge the request the attacker would need the token, which appears only in the bank's own pages. The **same-origin policy** forbids `evil.example`'s JavaScript from reading `bank.example`'s pages, so it cannot fetch the form to copy the token, and it cannot guess a random 256-bit value. The forged request has the cookie but not the token, so the server answers 400 and does nothing.

**3. `SameSite=Lax`.** With `Lax`, the browser does **not** send the cookie on cross-site POSTs and cross-site subresource requests (forms, images, `fetch`), so the forged POST arrives without a session. It still sends the cookie on top-level navigations with safe methods (clicking a link: GET). It is **not enough on its own** because: a state-changing GET would still work; an attacker on a sibling subdomain (same *site*) is not cross-site; older browsers ignore it; and a cookie with `SameSite=None` is sent everywhere. So use it together with tokens.

**4. GET must be safe.** A GET can be fired by anything: an `<img src>`, a link, a prefetch, and `Lax` cookies are sent with link clicks. A token cannot be demanded in those cases, so the only defence is the rule that **GET never changes data**.

**Checklist: your answer should mention**
- [ ] the browser sends the cookie automatically with every request to the bank, even one started by another site
- [ ] the attacker cannot read the cookie or the response, but only needs the side effect
- [ ] the token is not sent automatically: it must come from the bank's own page
- [ ] the **same-origin policy** stops the attacker's script from reading that page, so the token cannot be copied
- [ ] `SameSite=Lax` withholds the cookie on cross-site POSTs; not enough alone (state-changing GET, same-site attacker, old browsers)
- [ ] GET must never change data
