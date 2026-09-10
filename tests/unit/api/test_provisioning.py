from __future__ import annotations


def test_create_provisioning_job_requires_auth(api_client) -> None:
    response = api_client.post(
        '/v1/provisioning/jobs',
        json={'msisdn': 989121234567, 'first_name': 'Demo', 'last_name': 'User'},
    )
    assert response.status_code == 401


def test_create_provisioning_job(api_client, auth_headers) -> None:
    response = api_client.post(
        '/v1/provisioning/jobs',
        headers=auth_headers,
        json={'msisdn': 989121234567, 'first_name': 'Demo', 'last_name': 'User'},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload['state'] == 'QUEUED'
    assert payload['msisdn'] == 989121234567


def test_agent_claim_requires_token(api_client) -> None:
    response = api_client.post(
        '/v1/provisioning/agent/claim',
        headers={'X-Telorax-Agent-Id': 'android-1'},
        json={'provider': 'android-agent'},
    )
    assert response.status_code == 401


def test_submit_sms_code(api_client, auth_headers) -> None:
    created = api_client.post(
        '/v1/provisioning/jobs',
        headers=auth_headers,
        json={'msisdn': 989121234567, 'first_name': 'Demo', 'last_name': 'User'},
    )
    job_id = created.json()['id']
    response = api_client.post(
        f'/v1/provisioning/jobs/{job_id}/sms-code',
        headers=auth_headers,
        json={'sms_code': '12345'},
    )
    assert response.status_code == 200
    assert response.json()['metadata']['sms_code'] == '12345'
