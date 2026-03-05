"""API Gateway with rate limiting and quota management.

Handles incoming API requests through a middleware pipeline:
  1. Authentication (validate API key)
  2. Quota cost calculation (determine per-request quota cost)
  3. Quota check (enforce per-user request limits)
  4. Rate limiting (enforce per-window request limits)
  5. Backend routing (forward to appropriate service)
"""

from dataclasses import dataclass, field

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
class RequestContext:
    """Carries request data and mutable state through the middleware pipeline.

    Middleware can read request fields and write to the state dict
    during evaluate/commit phases.
    """

    request_id: str
    user_id: str
    api_key: str
    path: str
    method: str
    timestamp: float
    body: dict | None = None

    # Pipeline state — written by middleware during processing
    state: dict = field(default_factory=dict)

    # Set by middleware to halt the pipeline with an error response
    rejected: bool = False
    rejection_status: int = 0
    rejection_reason: str | None = None


@dataclass
class Response:
    """A response from the API gateway."""

    request_id: str
    status: int
    body: dict | None = None
    was_allowed: bool = True
    reason: str | None = None


class Middleware:
    """Base class for gateway middleware.

    Middleware participates in a two-phase processing pipeline:

      Phase 1 — evaluate(context):
        Inspect the request and determine whether it should proceed.
        This phase MUST be read-only with respect to external state.
        Set context.rejected = True to halt the pipeline.

      Phase 2 — commit(context):
        Apply side effects (consume quota, log metrics, etc.).
        Only called if the request was not rejected by any middleware.

    The engine runs all middleware through both phases in order. A request
    is only committed once every middleware has approved it.
    """

    def evaluate(self, context: RequestContext) -> None:
        """Phase 1: Read-only evaluation. May reject the request."""
        pass

    def commit(self, context: RequestContext) -> None:
        """Phase 2: Apply side effects for an approved request."""
        pass


class AuthMiddleware(Middleware):
    """Validates API keys against the authentication service."""

    def __init__(self, auth_service):
        self._EXT_auth_service = auth_service

    def evaluate(self, context: RequestContext) -> None:
        authenticated_user = self._EXT_auth_service.validate(context.api_key)
        if authenticated_user is None:
            context.rejected = True
            context.rejection_status = 401
            context.rejection_reason = "unauthorized"
        else:
            context.state["authenticated_user"] = authenticated_user


class QuotaCostCalculator(Middleware):
    """Determines the quota cost of each request based on its characteristics.

    Different operations consume different amounts of quota:
      - Read operations (GET, HEAD, OPTIONS): 1 unit
      - Write operations (POST, PUT, PATCH): 2 units
      - Destructive operations (DELETE): 3 units
      - Bulk endpoints (/api/batch/*): additional 2x multiplier

    This allows the gateway to weight expensive operations more heavily
    against a user's quota allocation.
    """

    WRITE_METHODS = {"POST", "PUT", "PATCH"}
    BASE_COSTS = {
        "GET": 1,
        "HEAD": 1,
        "OPTIONS": 1,
        "DELETE": 3,
    }
    BULK_PATH_PREFIX = "/api/batch"

    def evaluate(self, context: RequestContext) -> None:
        base_cost = self._compute_base_cost(context.method)
        multiplier = self._compute_multiplier(context.path)
        context.state["quota_cost"] = base_cost * multiplier
        

    def _compute_base_cost(self, method: str) -> int:
        """Look up the base cost for an HTTP method."""
        method_upper = method.upper()
        if method_upper in self.WRITE_METHODS:
            return 2
        return self.BASE_COSTS.get(method_upper, 1)

    def _compute_multiplier(self, path: str) -> int:
        """Apply a multiplier for bulk operation endpoints."""
        if path.lower().startswith(self.BULK_PATH_PREFIX):
            return 2
        return 1


class QuotaMiddleware(Middleware):
    """Enforces per-user  request quotas.

    Evaluate: checks if the user has enough remaining quota for the
        request's cost (determined by QuotaCostCalculator).
    Commit: consumes the calculated quota cost for approved requests.
    """

    def __init__(self, quota_service):
        self._EXT_quota_service = quota_service

    def evaluate(self, context: RequestContext) -> None:
        cost = context.state.get("quota_cost", 1)
        remaining = self._EXT_quota_service.get_remaining(context.user_id)
        if remaining < cost:
            context.rejected = True
            context.rejection_status = 429
            context.rejection_reason = "quota_exceeded"
        context.state["quota_remaining"] = remaining

    def commit(self, context: RequestContext) -> None:
        cost = context.state.get("quota_cost", 1)
        for _ in range(cost):
            self._EXT_quota_service.consume(context.user_id)
        context.state["quota_remaining"] = self._EXT_quota_service.get_remaining(
            context.user_id
        )


class RateLimitMiddleware(Middleware):
    """Sliding window rate limiter.

    Tracks per-user request timestamps and enforces a maximum number
    of requests within a rolling time window.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_log: dict[str, list[float]] = {}

    def evaluate(self, context: RequestContext) -> None:
        user_id = context.user_id
        timestamp = context.timestamp

        if user_id not in self.request_log:
            self.request_log[user_id] = []
        
        # Remove timestamps outside the current window
        window_start = timestamp - self.window_seconds
        self.request_log[user_id] = [
            t for t in self.request_log[user_id] if t > window_start
        ]

        current_count = len(self.request_log[user_id])
        if current_count >= self.max_requests:
            context.rejected = True
            context.rejection_status = 429
            context.rejection_reason = "rate_limited"
            return

        # Record this request
        self.request_log[user_id].append(timestamp)

        context.state["rate_limit_remaining"] = self.max_requests - current_count - 1


class MiddlewareEngine:
    """Executes the middleware pipeline against a request context.

    Processes each registered middleware in sequence, running both the
    evaluate and commit phases to completion before moving on.
    """

    def __init__(self):
        self.middleware: list[Middleware] = []

    def register(self, middleware: Middleware) -> None:
        """Add a middleware to the end of the pipeline."""
        self.middleware.append(middleware)

    def execute(self, context: RequestContext) -> None:
        """Run the middleware pipeline on the given context.

        Each middleware evaluates the request and, if approved,
        commits its side effects. Processing halts on first rejection.
        """
        for middleware in self.middleware:
            middleware.evaluate(context)
            if context.rejected:
                return
            middleware.commit(context)


class APIGateway:
    """API Gateway that processes requests through a middleware pipeline.

    Requests pass through authentication, classification, quota enforcement,
    and rate limiting before being routed to the backend service.
    """

    def __init__(self, rate_limit: int = 5, window_seconds: float = 10.0):
        self._EXT_auth_service = AuthService()
        self._EXT_quota_service = QuotaService()
        self._EXT_backend_service = BackendService()

        self.engine = MiddlewareEngine()
        self.engine.register(AuthMiddleware(self._EXT_auth_service))
        self.engine.register(QuotaCostCalculator())
        self.engine.register(QuotaMiddleware(self._EXT_quota_service))
        self.engine.register(RateLimitMiddleware(rate_limit, window_seconds))

    def register_user(self, user_id: str, api_key: str, quota: int):
        """Register a user with the gateway."""
        self._EXT_auth_service.register(user_id, api_key)
        self._EXT_quota_service.set_quota(user_id, quota)

    def handle_request(self, request: Request) -> Response:
        """Process an incoming API request through the middleware pipeline."""
        context = RequestContext(
            request_id=request.request_id,
            user_id=request.user_id,
            api_key=request.api_key,
            path=request.path,
            method=request.method,
            timestamp=request.timestamp,
            body=request.body,
        )
        
        self.engine.execute(context)

        if context.rejected:            

            return Response(
                request_id=context.request_id,
                status=context.rejection_status,
                body=None,
                was_allowed=False,
                reason=context.rejection_reason,
            )

        result = self._EXT_backend_service.handle(
            context.path,
            context.method,
            context.body,
        )
        return Response(
            request_id=context.request_id,
            status=200,
            body=result,
            was_allowed=True,
        )
