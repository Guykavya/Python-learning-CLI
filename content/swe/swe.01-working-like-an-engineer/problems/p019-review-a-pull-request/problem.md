# Review a pull request

A teammate opened a pull request "Add discount helper". This is the whole diff. Write the **review** in `answer.md`: **four comments**, each starting with a label (`blocking:`, `suggestion:`, `nit:` or `question:`), saying **what** you see, **why** it matters, and **how** you would fix it (chapter section 16.4 and 16.5). Be kind and specific; mention at least one thing that is good.

```diff
--- a/shop/pricing.py
+++ b/shop/pricing.py
@@ -1,9 +1,14 @@
 """Price helpers."""
 
 TAX_RATE = 0.18
 
 
-def apply_discount(price, percent):
-    return price - price * percent / 100
+def discount(price, percent):
+    d = price*percent/100
+    return price - d
+
+
+def total(prices, percent):
+    return sum(discount(p, percent) for p in prices)
 
 
 def with_tax(price):
     return round(price * (1 + TAX_RATE), 2)
--- a/shop/checkout.py
+++ b/shop/checkout.py
@@ -1,6 +1,6 @@
-from shop.pricing import apply_discount, with_tax
+from shop.pricing import discount, with_tax
 
 
 def final_price(price):
-    return with_tax(apply_discount(price, 10))
+    return with_tax(discount(price, 10))
```

The pull request description says only: "added discount, works for me". There are no changes in `tests/`.
