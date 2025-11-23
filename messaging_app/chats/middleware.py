import logging
from datetime import datetime
from django.http import HttpResponseForbidden

# Set up a logger
logger = logging.getLogger(__name__)
# Prevent logs from propagating to the root logger, which might have a different configuration
logger.propagate = False 
# Set the logging level
logger.setLevel(logging.INFO)

# Create a file handler to log to a file
handler = logging.FileHandler('requests.log')
# Create a formatter and set it for the handler
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger if it doesn't have one already
if not logger.handlers:
    logger.addHandler(handler)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log before processing the request
        user = request.user if request.user.is_authenticated else 'Anonymous'
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Process the request
        response = self.get_response(request)

        # You can also log after the request is processed if needed
        # For instance, logging the response status code
        # logger.info(f"Response status for {request.path}: {response.status_code}")

        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        # Restrict access between 9 PM (21:00) and 6 AM (06:00)
        if now.hour >= 21 or now.hour < 6:
            return HttpResponseForbidden("Access is restricted during this time.")
        
        response = self.get_response(request)
        return response
