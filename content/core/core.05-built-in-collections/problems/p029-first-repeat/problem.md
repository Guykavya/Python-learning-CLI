# First repeated word

Read one line of words. Find the first word whose **second** occurrence comes earliest, and
print where its first and second occurrences are (positions start at 1):

```
<word> at <first position> and <second position>
```

If no word repeats, print `No repeats`.

**Example**

Input:
```
red blue green blue red
```
Output:
```
blue at 2 and 4
```

`red` also repeats, but its second occurrence (position 5) comes later than `blue`'s (position 4).

The tests include a line of 100,000 words. Searching a list for every word is too slow; use a
dict that remembers where each word was first seen.
