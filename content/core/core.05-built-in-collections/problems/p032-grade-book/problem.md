# Grade book averages

Read lines of `name mark` until a line `end`. A name can appear many times. For each student,
print their average mark (1 decimal place) and how many marks they have:

```
<name>: <average> (<count> marks)
```

Sort by average, **highest first**; students with equal averages are in alphabetical order.
If there were no marks at all, print `No marks.` Always write the word `marks`, even for a
count of 1, to keep it simple.

**Example**

Input:
```
asha 80
ravi 70
asha 90
meena 85
ravi 100
end
```
Output:
```
asha: 85.0 (2 marks)
meena: 85.0 (1 marks)
ravi: 85.0 (2 marks)
```
