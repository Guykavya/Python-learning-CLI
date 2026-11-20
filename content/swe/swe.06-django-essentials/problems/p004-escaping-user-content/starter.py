from django.template import Template


def render_comment(text):
    # TODO: use a Django Template with the linebreaksbr filter.
    # This version pastes the text into the HTML unescaped: unsafe!
    return f'<p class="comment">{text}</p>'
