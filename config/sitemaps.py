import datetime
from calendar import timegm
from functools import wraps

from cms.models import Title
from cms.utils import get_current_site as cms_get_current_site
from cms.utils.i18n import get_public_languages
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import translation
from django.utils.http import http_date

LIMIT = settings.SITEMAPS_PAGE_PER_ITEM


def x_robots_tag_without_page(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        response["X-Robots-Tag"] = "noindex, noodp, noarchive"
        return response

    return inner


def x_robots_tag_with_page(func):
    @wraps(func)
    def inner(request, page, *args, **kwargs):
        response = func(request, page, *args, **kwargs)
        response["X-Robots-Tag"] = "noindex, noodp, noarchive"
        return response

    return inner


@x_robots_tag_without_page
def index(
    request,
    sitemaps,
    template_name="sitemap_index.xml",
    content_type="application/xml",
):
    req_protocol = request.scheme
    req_site = get_current_site(request)

    sites = {}  # all sections' sitemap URLs

    for section, site in sitemaps.items():
        # For each section label, add links of all pages of its sitemap
        # (usually generated by the `sitemap` view).
        if callable(site):
            site = site()

        protocol = req_protocol if site.protocol is None else site.protocol

        # Add links to all pages of the sitemap.
        for page in range(1, site.paginator.num_pages + 1):
            if page == 1:
                sitemap_url_name = "config.sitemaps.sitemap_without_page"
                sitemap_url = reverse(sitemap_url_name, kwargs={"section": section})
                absolute_url = "%s://%s%s" % (protocol, req_site.domain, sitemap_url)
                sites[absolute_url] = site.get_sitemaps_last_mode()
            else:
                sitemap_url_name = "config.sitemaps.sitemap_with_page"
                sitemap_url = reverse(
                    sitemap_url_name, kwargs={"section": section, "page": page}
                )
                absolute_url = "%s://%s%s" % (protocol, req_site.domain, sitemap_url)
                sites[absolute_url] = site.get_sitemaps_last_mode()

    return TemplateResponse(
        request,
        template_name,
        {"sitemaps": sites},
        content_type=content_type,
    )


@x_robots_tag_with_page
def sitemap_with_page(
    request,
    page,
    sitemaps,
    section=None,
    template_name="sitemap.xml",
    content_type="application/xml",
):

    req_protocol = request.scheme
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()

    lastmod = None
    all_sites_lastmod = True
    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_urls(page=page, site=req_site, protocol=req_protocol))
            if all_sites_lastmod:
                site_lastmod = getattr(site, "latest_lastmod", None)
                if site_lastmod is not None:
                    site_lastmod = (
                        site_lastmod.utctimetuple()
                        if isinstance(site_lastmod, datetime.datetime)
                        else site_lastmod.timetuple()
                    )
                    lastmod = (
                        site_lastmod if lastmod is None else max(lastmod, site_lastmod)
                    )
                else:
                    all_sites_lastmod = False
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    response = TemplateResponse(
        request, template_name, {"urlset": urls}, content_type=content_type
    )
    if all_sites_lastmod and lastmod is not None:
        # if lastmod is defined for all sites, set header so as
        # ConditionalGetMiddleware is able to send 304 NOT MODIFIED
        response["Last-Modified"] = http_date(timegm(lastmod))
    return response


@x_robots_tag_without_page
def sitemap_without_page(
    request,
    sitemaps,
    section=None,
    template_name="sitemap.xml",
    content_type="application/xml",
):

    req_protocol = request.scheme
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()

    lastmod = None
    all_sites_lastmod = True
    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_urls(page=1, site=req_site, protocol=req_protocol))
            if all_sites_lastmod:
                site_lastmod = getattr(site, "latest_lastmod", None)
                if site_lastmod is not None:
                    site_lastmod = (
                        site_lastmod.utctimetuple()
                        if isinstance(site_lastmod, datetime.datetime)
                        else site_lastmod.timetuple()
                    )
                    lastmod = (
                        site_lastmod if lastmod is None else max(lastmod, site_lastmod)
                    )
                else:
                    all_sites_lastmod = False
        except EmptyPage:
            raise Http404("Page %s empty" % 1)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % 1)
    response = TemplateResponse(
        request, template_name, {"urlset": urls}, content_type=content_type
    )
    if all_sites_lastmod and lastmod is not None:
        # if lastmod is defined for all sites, set header so as
        # ConditionalGetMiddleware is able to send 304 NOT MODIFIED
        response["Last-Modified"] = http_date(timegm(lastmod))
    return response


def from_iterable(iterables):
    """
    Backport of itertools.chain.from_iterable
    """
    for it in iterables:
        for element in it:
            yield element


class BaseSitemaps(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = LIMIT

    def get_query_filter(self):
        site = cms_get_current_site()
        languages = get_public_languages(site_id=site.pk)

        query_filter = Q()
        query_filter.add(Q(redirect="") | Q(redirect__isnull=True), Q.AND)
        query_filter.add(Q(language__in=languages), Q.AND)
        query_filter.add(Q(page__login_required=False), Q.AND)
        query_filter.add(Q(page__node__site=site), Q.AND)
        query_filter.add(Q(published=True), Q.AND)
        return query_filter

    def get_title_objects(self,query):
        return Title.objects.filter(query)

    def get_category_objects(self):
        query_filter = self.get_query_filter()
        query_filter.add(Q(page__type=2), Q.AND)
        query_filter.add(Q(page__is_home=True, page__publisher_is_draft=False), Q.OR)
        return self.get_title_objects(query_filter)

    def get_ringtone_objects(self):
        query_filter = self.get_query_filter()
        query_filter.add(Q(page__type=3), Q.AND)
        query_filter.add(Q(page__is_home=True, page__publisher_is_draft=False), Q.OR)
        return self.get_title_objects(query_filter)

    def get_page_objects(self):
        query_filter = self.get_query_filter()
        query_filter.add(Q(page__type=1), Q.AND)
        query_filter.add(Q(page__publisher_is_draft=False), Q.AND)
        query_filter.add(Q(page__is_home=False), Q.AND)
        query_filter.add(Q(Q(page__soft_root=True) | Q(page__in_navigation=True)), Q.AND)
        return self.get_title_objects(query_filter)

    def lastmod(self, title):
        modification_dates = [title.page.changed_date, title.page.publication_date]
        plugins_for_placeholder = lambda placeholder: placeholder.get_plugins()
        plugins = from_iterable(
            map(plugins_for_placeholder, title.page.placeholders.all())
        )
        plugin_modification_dates = map(lambda plugin: plugin.changed_date, plugins)
        modification_dates.extend(plugin_modification_dates)
        return max(modification_dates)

    def location(self, title):
        translation.activate(title.language)
        url = title.page.get_absolute_url(title.language)
        translation.deactivate()
        return url


class RingtoneSitemaps(BaseSitemaps):
    changefreq = "daily"
    priority = 1

    def items(self):        
        return self.get_ringtone_objects().order_by("page__node__path").distinct()
    
    def get_sitemaps_last_mode(self):
        return self.get_ringtone_objects().latest("page__changed_date").page.changed_date


class CategorySitemaps(BaseSitemaps):
    changefreq = "daily"
    priority = 1

    def items(self):
        return self.get_category_objects().order_by("page__node__path").distinct()

    def get_sitemaps_last_mode(self):
        return self.get_category_objects().latest("page__changed_date").page.changed_date

class PageSitemaps(BaseSitemaps):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return self.get_page_objects().order_by("page__node__path").distinct()
    
    def get_sitemaps_last_mode(self):
        return self.get_page_objects().latest("page__changed_date").page.changed_date

# sitemaps url
SITEMAP_URL = "sitemap.xml"
SITEMAP_SECTION_WO = "<section>.xml"
SITEMAP_SECTION_WITH = "<section>-<page>.xml"
SITEMAP_OBJECT = {
    "sitemaps": {
        "ringtone": RingtoneSitemaps,
        "category": CategorySitemaps,
        "page": PageSitemaps,
    }
}

SITEMAPS = [
    path(
        SITEMAP_URL,
        index,
        SITEMAP_OBJECT,
        name="config.sitemaps.index",
    ),
    path(
        SITEMAP_SECTION_WITH,
        sitemap_with_page,
        SITEMAP_OBJECT,
        "config.sitemaps.sitemap_with_page",
    ),
    path(
        SITEMAP_SECTION_WO,
        sitemap_without_page,
        SITEMAP_OBJECT,
        "config.sitemaps.sitemap_without_page",
    ),
]
