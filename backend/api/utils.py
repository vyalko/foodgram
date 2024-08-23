from django.shortcuts import get_object_or_404, redirect

from recipes.models import ShortLink


def redirect_short_link(request, short_url):
    short_link = get_object_or_404(
        ShortLink, short_url=short_url
    )
    return redirect(short_link.original_url)