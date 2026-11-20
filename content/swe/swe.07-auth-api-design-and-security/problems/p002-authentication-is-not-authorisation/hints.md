## Hint 1

Think of a hotel. The ID check at the desk and the key card that opens only **your** room are two different things. Which one is authentication and which one is authorisation? What does "identification" add, before the check?

## Hint 2

For the bug, imagine `GET /orders/5` where the server asks only "is the token valid?". User 1 owns order 1. What happens when user 1 changes the number in the URL? Which of the six questions did the developer skip?

## Hint 3

```text
1. identification = claim (username) | authentication = proof | authorisation = permission for this object
2. accountability = audit log (who, what, which object, when); needs trustworthy authentication
3. bug: valid token, no owner check -> /orders/2 readable by user 1; fix: scope by owner, deny by default
4. six questions: who? may they? inputs ok? cost? twice? log/leak?  (authn = 1, authz = 2)
```
