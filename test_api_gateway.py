"""Tests for API Gateway rate limiting and quota behavior.

Simulates realistic traffic patterns across multiple users to verify
that the gateway correctly handles rate limiting without corrupting
quota state.
"""

from api_gateway import APIGateway, Request


def make_request(request_id, user_id, timestamp, path="/api/data"):
    """Create a request with standard defaults."""
    return Request(
        request_id=f"req_{request_id:03d}",
        user_id=user_id,
        api_key=f"key_{user_id}",
        path=path,
        method="GET",
        timestamp=timestamp,
    )


def test_rate_limited_requests_preserve_quota():
    """Rate-limited requests should not consume quota.

    Scenario:
    - 4 users each have a quota of 50 requests
    - Rate limit: 5 requests per 10-second window
    - Alice sends steady traffic (1 req / 3s) — never hits rate limit
    - Bob sends bursts (8 reqs every 15s) — hits rate limit each burst
    - Charlie sends moderate traffic (3 reqs / 8s) — stays under rate limit
    - Diana sends steady traffic (1 req / 2.5s) — never hits rate limit

    Expected behavior:
    - Bob gets rate_limited on his 6th-8th request in each burst
    - Rate-limited requests should NOT consume quota
    - No user should ever see quota_exceeded, since each user makes
      fewer than 50 *successful* requests total
    """
    gateway = APIGateway(rate_limit=5, window_seconds=10.0)

    # Register users with generous quotas
    gateway.register_user("alice", "key_alice", quota=50)
    gateway.register_user("bob", "key_bob", quota=50)
    gateway.register_user("charlie", "key_charlie", quota=50)
    gateway.register_user("diana", "key_diana", quota=50)

    # Build the timeline of requests
    all_requests = []

    # Alice: 1 request every 3 seconds for 120 seconds (40 requests)
    for i in range(40):
        all_requests.append(("alice", i * 3.0))

    # Bob: bursts of 8 requests every 15 seconds (64 requests)
    for burst_start in range(0, 120, 15):
        for j in range(8):
            all_requests.append(("bob", burst_start + j * 0.5))

    # Charlie: 3 requests every 8 seconds (45 requests)
    for group_start in range(0, 120, 8):
        for j in range(3):
            all_requests.append(("charlie", group_start + j * 1.0))

    # Diana: 1 request every 2.5 seconds (48 requests)
    for i in range(48):
        all_requests.append(("diana", i * 2.5))

    # Sort by timestamp to simulate realistic interleaving
    all_requests.sort(key=lambda x: x[1])

    # Process all requests
    results = []
    for req_id, (user_id, timestamp) in enumerate(all_requests):
        request = make_request(req_id, user_id, timestamp)
        response = gateway.handle_request(request)
        results.append(
            {
                "request_id": request.request_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "was_allowed": response.was_allowed,
                "reason": response.reason,
                "status": response.status,
            }
        )

    # Verify no user was blocked for quota exhaustion
    quota_blocked = [r for r in results if r["reason"] == "quota_exceeded"]

    # Count successful requests per user for context in failure message
    successful_per_user = {}
    for r in results:
        if r["was_allowed"]:
            successful_per_user[r["user_id"]] = (
                successful_per_user.get(r["user_id"], 0) + 1
            )

    assert len(quota_blocked) == 0, (
        f"Found {len(quota_blocked)} requests incorrectly blocked for quota exhaustion.\n"
        f"Successful requests per user: {successful_per_user}\n"
        f"First quota_exceeded: {quota_blocked[0] if quota_blocked else 'none'}"
    )


def test_all_users_can_complete_normal_workload():
    """Each user should be able to complete a normal workload within quota.

    Simulates a scenario where each user sends requests at a moderate,
    sustained rate that stays within rate limits. All requests should
    succeed and quota should decrease predictably.
    """
    gateway = APIGateway(rate_limit=5, window_seconds=10.0)

    gateway.register_user("alice", "key_alice", quota=50)
    gateway.register_user("bob", "key_bob", quota=50)
    gateway.register_user("charlie", "key_charlie", quota=50)
    gateway.register_user("diana", "key_diana", quota=50)

    # Each user sends 30 requests at a steady rate (well within rate limit)
    all_requests = []
    for user in ["alice", "bob", "charlie", "diana"]:
        for i in range(30):
            # 1 request every 3 seconds — under 5/10s rate limit
            all_requests.append((user, i * 3.0))

    all_requests.sort(key=lambda x: x[1])

    blocked = []
    for req_id, (user_id, timestamp) in enumerate(all_requests):
        request = make_request(req_id, user_id, timestamp)
        response = gateway.handle_request(request)
        if not response.was_allowed:
            blocked.append(
                {
                    "request_id": request.request_id,
                    "user_id": user_id,
                    "timestamp": timestamp,
                    "reason": response.reason,
                }
            )

    assert len(blocked) == 0, (
        f"Expected all requests to succeed but {len(blocked)} were blocked.\n"
        f"First blocked: {blocked[0]}"
    )
