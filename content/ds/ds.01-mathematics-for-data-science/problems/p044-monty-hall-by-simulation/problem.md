# Monty Hall by simulation

Chapter section 9.5. There are three doors: one hides a car, two hide goats. You pick a door; the host, who knows where the car is, opens a **different door with a goat**; then you may **switch** to the remaining closed door or **stay**. Simulation settles the argument.

Write `monty_hall(switch, trials, seed)` returning the **fraction of trials in which you win the car**. Use `rng = np.random.default_rng(seed)`; each trial picks a random car door and a random first choice, the host opens a goat door that is neither, and you stay or switch according to `switch`.

## Example

```text
monty_hall(switch=False, trials=20000, seed=0)  ->  about 0.333
monty_hall(switch=True,  trials=20000, seed=0)  ->  about 0.667
```
