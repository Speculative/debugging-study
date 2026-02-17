"""External service interfaces (simplified for testing).

These simulate the behavior of real external services that the API gateway
depends on: authentication, quota management, and backend routing.
In production, these would be separate microservices accessed over the network.
"""


class AuthService:
    """Authentication service that validates API keys."""

    def __init__(self):
        self._keys = {}  # api_key -> user_id

    def register(self, user_id, api_key):
        """Register an API key for a user."""
        self._keys[api_key] = user_id

    def validate(self, api_key):
        """Check if an API key is valid. Returns the associated user_id or None."""
        return self._keys.get(api_key)


class QuotaService:
    """Quota management service that tracks per-user request allowances."""

    def __init__(self):
        self._quotas = {}  # user_id -> {"limit": int, "remaining": int}

    def set_quota(self, user_id, limit):
        """Set the quota for a user."""
        self._quotas[user_id] = {"limit": limit, "remaining": limit}

    def get_remaining(self, user_id):
        """Get remaining quota for a user. Returns 0 if user not found."""
        if user_id not in self._quotas:
            return 0
        return self._quotas[user_id]["remaining"]

    def consume(self, user_id):
        """Consume one unit of quota. Returns the new remaining count."""
        if user_id not in self._quotas:
            return 0
        self._quotas[user_id]["remaining"] = max(
            0, self._quotas[user_id]["remaining"] - 1
        )
        return self._quotas[user_id]["remaining"]

    def get_limit(self, user_id):
        """Get the total quota limit for a user."""
        if user_id not in self._quotas:
            return 0
        return self._quotas[user_id]["limit"]


class BackendService:
    """Backend API service that handles actual request processing."""

    def handle(self, path, method, body=None):
        """Process a request and return a response body."""
        return {"status": "ok", "path": path, "method": method}
