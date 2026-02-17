"""API Gateway with rate limiting and quota management.

Handles incoming API requests through a pipeline:
  1. Authentication (validate API key)
  2. Quota check (enforce per-user request limits)
  3. Rate limiting (enforce per-window request limits)
  4. Backend routing (forward to appropriate service)
"""

from dataclasses import dataclass, field

import autopsy

from external_services import AuthService, BackendService, QuotaService


@dataclass
class Request:
    """An incoming API request."""

    request_id: str
    user_id: str
    api_key: str
    path: str
    method: str
    timestamp: float
    body: dict | None = None


@dataclass
class Response:
    """A response from the API gateway."""

    request_id: str
    status: int
    body: dict | None = None
    was_allowed: bool = True
    reason: str | None = None


class RateLimiter:
    """Sliding window rate limiter.

    Tracks per-user request timestamps and enforces a maximum number
    of requests within a rolling time window.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._request_log: dict[str, list[float]] = {}

    def check(self, user_id: str, timestamp: float) -> tuple[bool, int]:
        """Check if a request is within the rate limit.

        Returns (allowed, remaining_in_window).
        """
        if user_id not in self._request_log:
            self._request_log[user_id] = []

        # Remove timestamps outside the current window
        window_start = timestamp - self.window_seconds
        self._request_log[user_id] = [
            t for t in self._request_log[user_id] if t > window_start
        ]

        current_count = len(self._request_log[user_id])
        remaining = self.max_requests - current_count

        if remaining <= 0:
            return False, 0

        # Record this request
        self._request_log[user_id].append(timestamp)
        return True, remaining - 1


class APIGateway:
    """API Gateway that handles authentication, rate limiting, and routing.

    Processes requests through a pipeline of checks before forwarding
    to the backend service.
    """

    def __init__(self, rate_limit: int = 5, window_seconds: float = 10.0):
        self._EXT_auth_service = AuthService()
        self._EXT_quota_service = QuotaService()
        self._EXT_backend_service = BackendService()
        self._rate_limiter = RateLimiter(rate_limit, window_seconds)

    def register_user(self, user_id: str, api_key: str, quota: int):
        """Register a user with the gateway."""
        self._EXT_auth_service.register(user_id, api_key)
        self._EXT_quota_service.set_quota(user_id, quota)

    def handle_request(self, request: Request) -> Response:
        """Process an incoming API request through the gateway pipeline."""
        # Step 1: Authenticate
        authenticated_user = self._EXT_auth_service.validate(request.api_key)
        if authenticated_user is None:
            return self.send_response(request, 401, reason="unauthorized")

        # Step 2: Check quota
        quota_remaining = self._EXT_quota_service.get_remaining(request.user_id)
        if quota_remaining <= 0:
            return self.send_response(
                request, 429, reason="quota_exceeded", quota_remaining=0
            )

        # Step 3: Consume quota
        new_remaining = self._EXT_quota_service.consume(request.user_id)

        # Step 4: Check rate limit
        rate_allowed, window_remaining = self._rate_limiter.check(
            request.user_id, request.timestamp
        )
        if not rate_allowed:
            return self.send_response(
                request,
                429,
                reason="rate_limited",
                quota_remaining=new_remaining,
            )

        # Step 5: Route to backend
        result = self._EXT_backend_service.handle(request.path, request.method, request.body)

        return self.send_response(
            request, 200, body=result, quota_remaining=new_remaining
        )

    def send_response(self, request, status, body=None, reason=None, quota_remaining=None):
        """Build a response and log the request processing result."""
        was_allowed = status == 200

        return Response(
            request_id=request.request_id,
            status=status,
            body=body,
            was_allowed=was_allowed,
            reason=reason,
        )
