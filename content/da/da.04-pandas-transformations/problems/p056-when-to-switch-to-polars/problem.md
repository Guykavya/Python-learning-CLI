# When to switch to Polars

Chapter sections 13.1, 13.6, 13.7 and 13.8. Your team lead read a blog post: "Polars is 10 times faster than pandas.
We should rewrite all our analysis in Polars." In the chapter, one group-by on 2 million rows took 84.9 ms in pandas
and 56.3 ms in Polars on one machine (machine-specific).

Write a short, honest recommendation in `answer.md`, about 250 to 350 words:

1. What is really different about Polars (name at least three differences from section 13.1), and which of them help
   with speed or with fewer bugs?
2. What does the chapter's measurement show, and what does it **not** show? How would you decide for *your* team's
   workload?
3. When would you stay with pandas, when would you choose Polars, and is there a middle way?
4. Whatever library you use, which habits from this chapter do not change?

## Example

A start: "One query on one machine, 85 ms against 56 ms, is a hint, not a law. Before rewriting anything I would time
our own three slowest steps on our own data, in both libraries, and first check that the answers are equal..."
