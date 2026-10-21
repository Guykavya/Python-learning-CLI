# Sort words four ways

Read one line of words. Print four lines:

```
Plain: <sorted with no key>
Ignoring case: <sorted with key=str.lower>
By length: <shortest first>
Longest first: <longest first>
```

When two words tie (same lowercase form, or same length), they must stay in their **input
order**. Python's sort is stable, so `sorted(words, key=len)` and
`sorted(words, key=len, reverse=True)` already do this.

**Example**

Input:
```
pear Fig apple kiwi date
```
Output:
```
Plain: Fig apple date kiwi pear
Ignoring case: apple date Fig kiwi pear
By length: Fig pear kiwi date apple
Longest first: apple pear kiwi date Fig
```

In plain sorting, every uppercase letter comes before every lowercase letter, so `Fig` is first.
