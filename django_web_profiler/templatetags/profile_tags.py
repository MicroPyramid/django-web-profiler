from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_page(context, page, no_pages):
    if page <= 3:
        start_page = 1
    else:
        start_page = page - 3

    if no_pages <= 6:
        end_page = no_pages
    else:
        end_page = start_page + 6

    if end_page > no_pages:
        end_page = no_pages

    pages = range(start_page, end_page + 1)
    return pages
