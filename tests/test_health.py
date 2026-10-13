"""Tests for the /health endpoint."""


def test_health_endpoint(client):
    """Health endpoint should return 200 with status healthy."""
    rv = client.get("/health")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "healthy"
