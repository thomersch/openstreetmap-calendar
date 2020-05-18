def cors_any(handler):
    def wrapper(*args, **kwargs):
        resp = handler(*args, **kwargs)
        resp['Access-Control-Allow-Origin'] = '*'
        return resp
    return wrapper
