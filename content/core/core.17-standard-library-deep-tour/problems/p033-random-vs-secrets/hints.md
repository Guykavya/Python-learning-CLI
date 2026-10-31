## Hint 1

For each job, ask two questions: "What harm is done if someone can predict the next value?" and
"Do I ever need the *same* sequence again?" If the first answer is "an account is taken over",
it is `secrets`. If the second is "yes", it must be a seeded `random.Random`.

## Hint 2

The Mersenne Twister keeps 624 numbers of internal state, and each output reveals part of it
in a way that can be reversed. What does an attacker who collects 624 outputs know? And how many
seeds does an attacker need to try if the seed was `int(time.time())` from some time today?

## Hint 3

For the last question, think about what `random.seed(42)` inside a library does to the program
that imported it: is there one generator per module, or one shared by everyone?
