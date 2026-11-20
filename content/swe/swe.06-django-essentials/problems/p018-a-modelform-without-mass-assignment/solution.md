## Approach

```python
SKU_PATTERN = re.compile(r"^[A-Z]{2,4}-\d{3,5}$")


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "sku", "price", "category"]

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip().upper()
        if not SKU_PATTERN.match(sku):
            raise forms.ValidationError("A sku looks like AB-123: 2-4 letters, a hyphen, 3-5 digits.")
        return sku
```

- **Mass assignment.** A `ModelForm` copies every posted value that matches a form field into the model. If `quantity` (or `is_staff` in a user form) is a form field, a visitor only has to add `quantity=999` to the POST, no matter what your HTML page shows. With `fields = [...]` the field does not exist in the form, so Django never reads it. The allow-list also protects the future: a new model field stays out of the form until you add it on purpose. `exclude = ["quantity"]` is a deny-list and fails exactly then.
- **Order of validation.** For each field Django runs `to_python`, the validators, then `clean_<field>`. After all fields it runs the model's checks (`validate_unique`) on the **cleaned** data. That is why `"ab-123"` is turned into `"AB-123"` first and then found as a duplicate. When you edit an existing item, the form passes `instance=` and the uniqueness check excludes that row, so an item does not clash with itself.
- `clean_sku` must **return** the value; returning `None` would store `None`. Raising `ValidationError` puts the message in `form.errors["sku"]`.
- `form.save()` creates the row, with the model's default for every field that is not in the form (`quantity` = 0).

## Complexity

Constant work per field; `validate_unique` and the category check each run one query.

## Another way

You could put the pattern on the model with `validators=[RegexValidator(...)]`: the admin and every ModelForm then enforce it, but the normalising (`upper()`) still needs `clean_sku` or an override of `save()`. A database `CheckConstraint` with a regex works on PostgreSQL only. Keep the form check for friendly messages and a constraint for the truth.
