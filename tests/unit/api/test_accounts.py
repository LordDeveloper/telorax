from __future__ import annotations


def test_list_accounts_requires_auth(api_client) -> None:
    response = api_client.get('/v1/accounts')
    assert response.status_code == 401


def test_list_accounts(api_client, auth_headers) -> None:
    response = api_client.get('/v1/accounts', headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['total'] == 1
    assert payload['items'][0]['msisdn'] == 989121234567


def test_account_stats(api_client, auth_headers) -> None:
    response = api_client.get('/v1/accounts/stats', headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['operational'] == 1


def test_get_account(api_client, auth_headers) -> None:
    response = api_client.get('/v1/accounts/1', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['telegram_username'] == 'demo'


def test_import_session(api_client, auth_headers) -> None:
    response = api_client.post(
        '/v1/accounts/import',
        headers=auth_headers,
        files={'file': ('session.session', b'fake-session-bytes', 'application/octet-stream')},
        data={'renew': 'false'},
    )
    assert response.status_code == 201
    assert response.json()['created'] is True
