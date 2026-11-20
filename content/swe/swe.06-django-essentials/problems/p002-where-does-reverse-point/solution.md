## Approach

Read the URLconf from the top, and for each `reverse` call split the name at the colon.

```text
1: /blog/hello/
2: /blog/archive/2024/
3: /store/item/7/
4: /outlet/
5: NoReverseMatch
6: NoReverseMatch
```

- **1.** `blog:post`: the include `include((blog_patterns, "blog"))` creates the namespace `blog`. The pattern `<slug:slug>/` is named `post`; with the prefix `blog/` the URL is `/blog/hello/`.
- **2.** `blog:archive` takes one positional argument (`args=[2024]`); the converter `<int:year>` fills it: `/blog/archive/2024/`.
- **3.** `shop_patterns` is a tuple `(patterns, "shop")`, so its **app name** is `shop`. The first include (`store/`) has no `namespace=`, so its **instance namespace** is also `shop`. When you reverse `shop:...`, Django prefers the instance whose name equals the app name: `/store/item/7/`.
- **4.** `outlet` is the instance namespace of the second include, so `outlet:index` is `outlet/` + the empty pattern: `/outlet/`.
- **5.** `post` without a namespace is looked up at the top level. Only `home` is there, so `NoReverseMatch`.
- **6.** `<int:pk>` accepts only digits, so `"abc"` cannot be put into the URL. `reverse` raises `NoReverseMatch`, the same error as for an unknown name.

Real output of the program, run with Django 6.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Print `resolve("/store/item/7/")` and look at `.view_name` and `.namespaces`: it is the same lookup run in the other direction, and it is the quickest way to see which namespaces a URL belongs to.
