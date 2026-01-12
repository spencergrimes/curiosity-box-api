"""Rate limiting for API endpoints."""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AIQuestionRateThrottle(UserRateThrottle):
    """Rate limit per child (not per user) to control API costs."""

    scope = "ai_questions"

    def get_cache_key(self, request, view):
        """Use child_id for rate limit key instead of user."""
        # Only apply to the 'ask' action
        if view.action != "ask":
            return None

        # Rate limit per child, not per user/IP
        if hasattr(request, "data") and "child_id" in request.data:
            child_id = request.data.get("child_id")
            return f"throttle_ai_child_{child_id}"

        # Fallback to default behavior if no child_id
        return super().get_cache_key(request, view)

    def allow_request(self, request, view):
        """
        Check if the request should be allowed based on rate limit.

        Returns True if within limit, False if rate limited.
        """
        # Only throttle POST requests to the ask endpoint
        if request.method != "POST" or view.action != "ask":
            return True

        return super().allow_request(request, view)
