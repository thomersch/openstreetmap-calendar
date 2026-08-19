from functools import wraps

from django.utils.cache import patch_cache_control, patch_vary_headers


def mark_cacheable(response, max_age, vary_on_language=False):
    """
    Whitelist a response for CDN caching. Everything is private/no-store by
    default (see osmcal.middlewares.cache_policy_middleware); call this
    where a view has already decided its response is safe to cache publicly.

    The response must never carry a cookie (session, CSRF, auth) - if it
    does, CachePolicyMiddleware will raise rather than let a public
    response with a Set-Cookie header reach the CDN.

    vary_on_language must be set for anything whose output depends on
    Accept-Language (e.g. views using osmcal.api.decorators.language_from_header),
    otherwise the CDN will cache one language and serve it to everyone.

    For views whose output differs for logged-in users, only call this when
    request.user isn't authenticated - deciding that at the call site, where
    request is already in scope, keeps it explicit instead of having this
    helper guess where "the request" is.
    """
    patch_cache_control(response, public=True, max_age=max_age)
    if vary_on_language:
        patch_vary_headers(response, ["Accept-Language"])
    return response


def cacheable(max_age, vary_on_language=False):
    """
    Decorator form of mark_cacheable for views that are unconditionally
    public - e.g. static informational pages that never vary by who's
    asking. If a view's output depends on the requesting user, don't use
    this; call mark_cacheable directly in the view body instead.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            response = view_func(*args, **kwargs)
            return mark_cacheable(response, max_age, vary_on_language=vary_on_language)

        return wrapper

    return decorator
