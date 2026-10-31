- Saying the HTML regex "just needs to be improved". Every fix (single quotes, other attributes,
  comments, line breaks) uncovers another case; the honest answer is a parser.
- Claiming JSON can be handled with `.*?` lazy matches. Nested objects and escaped quotes inside
  strings still break it.
- Thinking `^\(.*\)$` checks balance because it "has brackets at both ends". It checks only the
  first and last characters.
- Saying "regex can't count" without explaining: the point is *unlimited* counting; a regex can
  check a fixed depth like two levels, never any depth.
- Forgetting the cases where regex is unnecessary (d, e). They are not bugs, but code that uses a
  regex for `endswith` is harder to read and easier to get wrong.
