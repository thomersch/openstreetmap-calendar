from django.utils.cache import patch_cache_control


def _cache_control_directives(response):
    directives = {}
    for directive in response.get("Cache-Control", "").split(","):
        directive = directive.strip()
        if not directive:
            continue
        key, _, value = directive.partition("=")
        directives[key.strip().lower()] = value.strip() if value else True
    return directives


class CachePolicyMiddleware:
    """
    Default-deny caching: a response is private/no-store unless a view
    explicitly opted in (see osmcal.cache.cacheable), which sets its own
    Cache-Control. That way a view that forgets to opt in just misses the
    CDN cache instead of accidentally becoming cacheable.

    If a view *did* opt in but the response also sets a cookie (e.g. it
    unexpectedly touched the session or CSRF token), refuse to serve it
    rather than risk a CDN caching one user's session/CSRF cookie and
    replaying it to another visitor.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        directives = _cache_control_directives(response)
        if not directives:
            patch_cache_control(response, private=True, no_store=True)
        elif directives.get("public") and response.cookies:
            raise RuntimeError(
                f"{request.path} is marked Cache-Control: public but also sets a cookie "
                "(Set-Cookie present). Refusing to risk caching a session/CSRF token."
            )

        return response
