## Hint 1

Which block of a `for` loop in Jinja runs when the sequence is empty? And where do filters go in `{{ ... }}`?

## Hint 2

Filters follow a pipe: `{{ post.title|title }}`, `{{ post.body|truncate(40) }}`. A date object has the method `strftime`, which you can call inside `{{ ... }}`: `{{ post.created.strftime("%d %b %Y") }}`.

## Hint 3

```text
{% for post in posts %}
  <li class="post"> <h2>title|title</h2> <time>strftime</time> <p class="summary">body|truncate(40)</p> </li>
{% else %}
  <li class="empty">No posts yet.</li>
{% endfor %}
```
