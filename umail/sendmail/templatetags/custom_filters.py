from django import template
import random

register = template.Library()


@register.filter
def truncate_email(email):
    local_part = email.split("@")[0]
    return " ".join(local_part.split()[:5])


@register.filter
def random_color(email):
    colors = [
        "#FF5733",
        "#33FF57",
        "#3357FF",
        "#FF33A1",
        "#FF8F33",
        "#33FFF5",
        "#8D33FF",
        "#FF3333",
        "#33FF8F",
        "#FF5733",
    ]
    return random.choice(colors)
