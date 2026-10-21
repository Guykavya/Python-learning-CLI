## Hint 1

List the borders. Ages 4 and 5 are on opposite sides of one. Which are the other two pairs?

## Hint 2

Make a table of eight ages and their prices: 0, 4, 5, 12, 13, 59, 60 and a typical one in the middle of each range. Which of these would catch a border moved by one year?

## Hint 3

```
ages and prices: 0->0, 4->0, 5->50, 12->50, 13->100, 59->100, 60->60, 90->60
also: with pytest.raises(ValueError): ticket_price(-1)
```
