## Hint 1

For each call, first split the name: `"blog:post"` means namespace `blog`, name `post`. Does a namespace with that label exist? Which `include(...)` created it? Then find the `path()` with that name inside that include and join the prefixes in order (outer prefix first).

## Hint 2

A name inside an `include` with a namespace can only be reached **with** the namespace: plain `"post"` is looked up at the top level of the project, where only `home` lives. For the namespace `shop`: the app name is `"shop"`, and the first include has no `namespace=`, so its instance namespace defaults to the app name. The second include has `namespace="outlet"`. Last, an `<int:pk>` converter accepts only digits; what does `reverse` do with `"abc"`?

## Hint 3

```text
1  blog:post  slug=hello      -> prefix blog/ + hello/            -> /blog/hello/
2  blog:archive args=[2024]   -> prefix blog/ + archive/2024/     -> /blog/archive/2024/
3  shop:item pk=7             -> default instance is store/       -> /store/item/7/
4  outlet:index               -> prefix outlet/ + ""              -> /outlet/
5  post (no namespace)        -> not a top-level name             -> NoReverseMatch
6  shop:item pk="abc"         -> int converter needs digits       -> NoReverseMatch
```
