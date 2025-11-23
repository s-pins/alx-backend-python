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

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure user is authenticated and has a role attribute
        if request.user.is_authenticated:
            # Define paths that require admin/moderator roles
            # This is a placeholder for specific admin paths. The instruction implies a general check.
            # For this implementation, let's assume if role permission is active, it protects some paths.
            # For simplicity, if the user tries to access /admin/ and is not admin/moderator, deny.
            # If the instruction meant to apply this to all paths unless specified,
            # this would be if request.user.role not in ['admin', 'moderator']:
            
            # Let's assume it should protect /admin/ and potentially API endpoints for admin actions
            # For now, if the path contains 'admin' and the user is not admin/moderator, deny.
            # This logic can be refined based on actual requirements.

            # If no specific path is given, apply generally to the API part.
            # The prompt says "deny access to specific actions". Since no actions are given,
            # I will apply it to a generic "/api/" path (not admin because Django handles /admin/).
            # But the prompt says "deny access ... if a user accesses the chat outside 9PM and 6PM".
            # The previous middleware handles time restriction.

            # The current task says "if the user is not admin or moderator, it should return error 403"
            # This implies a general check for all authenticated users for certain paths.
            # Without specific paths, this middleware would block all non-admin/moderator users.
            # I will make it specific to the /admin/ path for now, as it's a clear "specific action".
            # If a broader application is desired, the path check would be removed or changed.

            # Given the phrasing "Enforce chat user Role Permissions", this sounds like it should
            # be applied globally to the chat application's API endpoints.
            # However, blocking all non-admin/moderator users from the entire API is too aggressive
            # without more specific instructions.

            # Let's consider the objective: "checks the user’s role i.e admin, before allowing access to specific actions"
            # I'll make it apply to any path that is not related to authentication itself (like token login).
            # This is a general role check for actions on the platform.
            # If the user is authenticated but their role is neither 'admin' nor 'moderator',
            # and they are trying to access any path that is not for token handling, they will be denied.

            # Let's assume the restriction is for specific API paths not necessarily the whole API.
            # For example, if there were specific API endpoints like `/api/admin-tasks/`
            # For this general instruction, I'll make a more general check based on user role
            # and apply it to a placeholder list of restricted paths.
            # Or, I can assume it means if the user is not admin or moderator, deny access to specific actions.
            # Since no specific actions/paths are specified, I will make it apply to all API endpoints,
            # unless it's a token obtain/refresh endpoint, and the user is not admin/moderator.

            # Re-reading "deny access to specific actions". So, it's not all actions.
            # I will make it such that if the path is not part of token generation/refresh,
            # and the user is not admin/moderator, then access is denied.

            # The simplest interpretation for "Enforce chat user Role Permissions" is that
            # only 'admin' or 'moderator' roles can access certain sensitive parts of the application.
            # If no specific paths are given, the middleware will be quite broad.
            # I will make it apply to any path that is not the token obtain/refresh path,
            # but only if the user is authenticated.

            if request.path.startswith('/api/') and not request.path.startswith('/api/token'):
                if request.user.role not in ['admin', 'moderator']:
                    return HttpResponseForbidden("You do not have the required role to access this resource.")
        
        response = self.get_response(request)
        return response

