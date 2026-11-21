## Approach

The model answer is in `answer.md`. The structure that makes it good is **claim, evidence, cost**: for every benefit, say what you could point at to prove it (a measured test time, a count of SQL statements), and for every claim that sounds good but is weaker in practice (switching databases, faster tests), say so.

## Cost

Nothing to build. The skill is the honest list of section 6.4; a design review that cannot answer "which pain, which evidence?" for a layer has found a layer to postpone.

## Another way

Make it concrete in your own project (the "Try it" of section 3.4): run `grep -c "execute(" ` over your routes, time one rule test through HTTP and one through a function call, and write the two numbers next to the layer you are considering.
