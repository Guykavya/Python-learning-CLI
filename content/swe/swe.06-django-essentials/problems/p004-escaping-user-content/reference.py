from django.template import Context, Template

COMMENT = Template('<p class="comment">{{ text|linebreaksbr }}</p>')


def render_comment(text):
    return COMMENT.render(Context({"text": text}))
