## Hint 1

`Meta.fields` decides which model fields become form fields, and only form fields read data from the POST. Which is safer: a list of the fields you allow, or a list of the fields you remove? Which method of the form is called for the field `sku` after Django has converted the text?

## Hint 2

Use `fields = ["name", "sku", "price", "category"]`. Define `def clean_sku(self):` that reads `self.cleaned_data["sku"]`, applies `.strip().upper()`, checks it with `SKU_PATTERN.match(...)` (the starter has the compiled pattern), raises `forms.ValidationError("...")` if it does not match and **returns** the cleaned value. Django checks `unique=True` afterwards on the cleaned data, so the duplicate test works without more code.

## Hint 3

```text
class Meta: model = Item; fields = ["name", "sku", "price", "category"]

def clean_sku(self):
    sku = self.cleaned_data["sku"].strip().upper()
    if not SKU_PATTERN.match(sku): raise forms.ValidationError("...")
    return sku
```
