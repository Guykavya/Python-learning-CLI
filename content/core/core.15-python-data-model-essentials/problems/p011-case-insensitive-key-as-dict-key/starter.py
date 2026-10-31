class HeaderName:
    def __init__(self, text):
        self.text = text

    # TODO: __eq__ ignoring case (casefold), __hash__ consistent with it
    # TODO: __repr__ -> HeaderName('Content-Type'), __str__ -> the original text
