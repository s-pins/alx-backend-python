import logging
from datetime import datetime, timedelta
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

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_log = {}

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        # Only track POST requests to message-related endpoints
        if request.method == 'POST' and 'messages' in request.path:
            now = datetime.now()
            
            # Clean up old records for the current IP
            if ip_address in self.requests_log:
                self.requests_log[ip_address] = [
                    t for t in self.requests_log[ip_address] if now - t < timedelta(minutes=1)
                ]

            # Check if the user has exceeded the limit
            if ip_address in self.requests_log and len(self.requests_log[ip_address]) >= 5:
                return HttpResponseForbidden("You have sent too many messages. Please wait a moment.")

            # Log the new request
            if ip_address not in self.requests_log:
                self.requests_log[ip_address] = []
            self.requests_log[ip_address].append(now)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
