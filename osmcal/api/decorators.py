from django.utils import translation


def cors_any(handler):
    def wrapper(*args, **kwargs):
        resp = handler(*args, **kwargs)
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    return wrapper


def language_from_header(handler):
	def wrapper(obj, request, *args, **kwargs):
		translation.activate(translation.get_language_from_request(request))
		request.LANGUAGE_CODE = translation.get_language()
		r = handler(obj, request, *args, **kwargs)
		translation.deactivate()
		return r
	return wrapper
