## Hint 1

Which kind of check says "this value is one of the ones I wrote down"? What is the difference between that and checking "this value does not contain anything bad"? Which of the two can an attacker get around?

## Hint 2

For `limit`, three steps in this order: are all characters ASCII digits (`str.isascii()` and `str.isdigit()`)? Is the number in range? Only then convert. Why must `int(...)` come after the digit check and not before? Remember to check the **names** of the parameters too, before you look at their values.

## Hint 3

```text
unknown = params names not in {sort, status, limit}  -> ListingError naming it and listing the allowed names
sort = params.get("sort", "-created"); not in SORTS -> ListingError naming "sort" and listing SORTS
status = params.get("status"); if present and not in STATUSES -> ListingError
raw = params.get("limit", "20"); ASCII digits only and 1 <= int(raw) <= 100, else ListingError
return {"sort": sort, "status": status, "limit": int(raw)}
```
