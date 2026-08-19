from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from osmcal.cache import cacheable, mark_cacheable
from osmcal.middlewares.cache_policy_middleware import CachePolicyMiddleware


class CachePolicyMiddlewareTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_default_response_is_private_no_store(self):
        middleware = CachePolicyMiddleware(lambda request: HttpResponse())
        response = middleware(self.factory.get("/"))
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])

    def test_opted_in_view_is_publicly_cacheable(self):
        @cacheable(max_age=300)
        def view(request):
            return HttpResponse()

        middleware = CachePolicyMiddleware(view)
        response = middleware(self.factory.get("/"))
        self.assertIn("public", response["Cache-Control"])
        self.assertIn("max-age=300", response["Cache-Control"])

    def test_opted_in_view_varies_on_language_when_requested(self):
        @cacheable(max_age=300, vary_on_language=True)
        def view(request):
            return HttpResponse()

        middleware = CachePolicyMiddleware(view)
        response = middleware(self.factory.get("/"))
        self.assertIn("Accept-Language", response["Vary"])

    def test_public_response_with_cookie_is_rejected(self):
        @cacheable(max_age=300)
        def view(request):
            response = HttpResponse()
            response.set_cookie("sessionid", "leaked")
            return response

        middleware = CachePolicyMiddleware(view)
        with self.assertRaises(RuntimeError):
            middleware(self.factory.get("/"))


class MarkCacheableTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_response_becomes_publicly_cacheable(self):
        def view(request):
            response = HttpResponse()
            if not request.user.is_authenticated:
                mark_cacheable(response, max_age=60)
            return response

        request = self.factory.get("/")
        request.user = AnonymousUser()
        middleware = CachePolicyMiddleware(view)
        response = middleware(request)
        self.assertIn("public", response["Cache-Control"])

    def test_authenticated_response_stays_private(self):
        def view(request):
            response = HttpResponse()
            if not request.user.is_authenticated:
                mark_cacheable(response, max_age=60)
            return response

        request = self.factory.get("/")
        request.user = type("FakeAuthenticatedUser", (), {"is_authenticated": True})()
        middleware = CachePolicyMiddleware(view)
        response = middleware(request)
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])
