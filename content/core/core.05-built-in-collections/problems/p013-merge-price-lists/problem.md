# Merge two price lists

A shop has an old price list and a new one. Each is one line of `item=price` pairs separated
by spaces (prices are whole numbers). Either line may be empty.

Merge them so that the **new** price wins whenever an item is in both. Print every item of the
merged list sorted by item name:

```
<item>: <price>
```

Then print one more line listing the items whose price **changed** (in both lists with
different prices), sorted and separated by `, `:

```
Changed: <items>
```

or `Changed: none` if no price changed.

**Example**

Input:
```
pen=10 ink=40 pad=25
ink=45 pad=25 tape=15
```
Output:
```
ink: 45
pad: 25
pen: 10
tape: 15
Changed: ink
```
