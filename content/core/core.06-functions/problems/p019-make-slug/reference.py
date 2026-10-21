def make_slug(text, /, *, sep="-", max_length=None):
    """Return a lowercase URL slug of text."""
    cleaned = "".join(ch if ch.isalnum() else " " for ch in text.lower())
    slug = sep.join(cleaned.split())
    if max_length is not None:
        slug = slug[:max_length]
        while sep and slug.endswith(sep):
            slug = slug[:-len(sep)]
    return slug
