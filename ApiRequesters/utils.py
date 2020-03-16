def get_token_from_request(request):
    try:
        return request.META['HTTP_AUTHORIZATION'][7:]
    except (IndexError, KeyError):
        return None
