from django import template
from django.utils.safestring import mark_safe
import magic

register = template.Library()


@register.filter
def convert_react_class(request, value):
    ringtone_react = request.session.get(f"ringtone_react_{value}", None)
    return "fa fa-heart" if ringtone_react else "fa fa-heart-o"


@register.filter
def breadcrumb(request):
    url = request.get_full_path()
    html = """
    <li itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">
        <a itemprop="item" href="/" href=""><span itemprop="name">Home</span></a>
        <meta itemprop="position" content="1" />
    </li>
    """
    new_url = []
    if url:
        i = 1
        for item in url.split("/"):
            if not item or "?" in item or "en" in item:
                continue
            else:
                i += 1
                new_url.append(item)
                build_url = "/".join(item for item in new_url)
                dash_to_convert_text = item.replace("-", " ")
                html += f"""
                <li itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">
                    <a itemprop="item" href="/{build_url}/"><span itemprop="name">{str(dash_to_convert_text).capitalize()}</span></a>
                    <meta itemprop="position" content="{i}" />
                </li>
                """
    return mark_safe(html)


@register.filter
def convert_into_tag(request):
    url = request.get_full_path()
    tags = []
    if url:
        for item in url.split("/"):
            if not item or "?" in item or "en" in item:
                continue
            else:
                convert_into_undersocre = item.replace("-", "_")
                if convert_into_undersocre:
                    tags.append(f"#{convert_into_undersocre}")
    return ",".join(item for item in tags)

@register.filter
def get_mime_type(file):
    """
    Get MIME by reading the header of the file
    """
    return magic.from_buffer(file,mime=True) 