## Model answer

**Definitions.** *Identification* is **claiming** who you are: sending a username or a user id, with no proof (`username=asha` in `POST /login`). *Authentication* (authn) is **proving** the claim: the password, a token or a key that only Asha should have (the password check inside `POST /login`, or the token on every later request). *Authorisation* (authz) is deciding **what this proven identity is allowed to do**: "only the owner may cancel this order" (`DELETE /orders/5`). Authentication answers "who are you?"; authorisation answers "may you do this, to this object?". Passing the first says nothing about the second.

**Accountability.** To hold somebody responsible later, the system must keep an **audit log**: who (the user id taken from the authenticated identity, never from the request body), what they did, to which object, when and from where. The log is only as good as the authentication: if anyone can pretend to be Asha, the log accuses Asha for what somebody else did.

**The bug.** `GET /orders/{id}` checks that a valid token is present (authentication) and then loads the order by id with no owner check (no authorisation). User 1 asks for `/orders/2` and reads user 2's order. This is the IDOR bug of chapter 8. The fix is to authorise: find the order **scoped to the caller** and **deny by default** (answer 404 or 403 when it is not theirs).

**Six questions per endpoint.** (1) Who is calling? (authentication) (2) May they do this to this object? (authorisation, including ownership) (3) Is every input checked? (4) What can this cost? (rate and size limits) (5) What if it is called twice? (idempotency) (6) What do we log and what do we leak?

**Checklist: your answer should mention**
- [ ] identification is a claim without proof (a username)
- [ ] authentication is proving the claim (password, token, key)
- [ ] authorisation is deciding what the proven identity may do, including ownership of the object
- [ ] one example endpoint for each word
- [ ] accountability needs an audit log (who, what, which object, when) that depends on trustworthy authentication
- [ ] the bug: a valid login lets a user read or change another user's object because only authentication was done
- [ ] deny by default, and check ownership in the query
- [ ] the six questions, with question 1 = authentication and question 2 = authorisation
