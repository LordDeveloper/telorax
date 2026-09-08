from __future__ import annotations


def test_mobile_agent_register_requires_token(api_client) -> None:
    response = api_client.post(
        '/v1/mobile-agent/register',
        headers={'X-Telorax-Agent-Id': 'android-01'},
        json={'platform': 'android', 'arch': 'arm64', 'version': '0.1.0', 'capabilities': {}},
    )
    assert response.status_code == 401


def test_mobile_agent_register(api_client, auth_headers) -> None:
    headers = {
        **auth_headers,
        'X-Telorax-Agent-Id': 'android-01',
    }
    response = api_client.post(
        '/v1/mobile-agent/register',
        headers=headers,
        json={
            'platform': 'android',
            'arch': 'arm64',
            'version': '0.1.0',
            'capabilities': {'package_installed': True},
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'registered'
