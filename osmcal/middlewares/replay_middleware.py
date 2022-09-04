from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.db.utils import ProgrammingError
from django.http import HttpResponse


class ReplayMiddleware:
	def __init__(self, get_response):
		if not settings.WRITABLE_REGION:
			"""
			We're probably running on local or in a non-distributed scenario,
			so let's detach this middleware.
			"""
			raise MiddlewareNotUsed()

		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def process_exception(self, request, exception):
		if isinstance(exception, ProgrammingError):
			if settings.CURRENT_REGION == settings.WRITABLE_REGION:
				# We are already in the region, which supposed to be writable, so reraise:
				return None
			response = HttpResponse()
			self.mark_for_replay(response)
			return response

	def mark_for_replay(self, response):
		response.headers['fly-replay'] = f"region={settings.WRITABLE_REGION}"
