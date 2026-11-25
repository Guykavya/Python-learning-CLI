# Natural or surrogate key?

Chapter section 3.2. A new analyst proposes to identify QuickFix customers by their **phone number**, because "everyone
has one and it is already in every file". The billing system uses an internal `customer_id` that nobody ever sees.

In `answer.md`, in about 150 to 250 words:

1. Give at least **three** ways a phone number can fail as a key. Use real situations (a customer changes number,
   two people share a number, two systems write numbers differently).
2. Say why the internal `customer_id` is safer, and what it still cannot protect you from.
3. The data warehouse stores `customer_id` and also the phone number. What rule should it keep on the phone number
   column, and why?

## Example

A start: "A natural key comes from the real world and the real world changes. A customer who gets a new SIM keeps the same
`customer_id` but has a new phone number, so..."
