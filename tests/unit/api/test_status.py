from __future__ import annotations


def test_get_status(api_client) -> None:
    response = api_client.get('/v1/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'healthy'
    assert len(payload['components']) == 3


def test_health_check(api_client) -> None:
    response = api_client.get('/v1/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
