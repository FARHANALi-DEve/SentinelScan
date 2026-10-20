"""Owner-only workspace contract and secure regression cases."""
from fastapi.testclient import TestClient
from app.main import create_app


def client_at(tmp_path):
    return TestClient(create_app(db_path=str(tmp_path / 'workspace.sqlite'), allowed_hosts=''))


def setup(client):
    res = client.post('/api/auth/setup', json={'username':'farhan', 'password':'A_Strong_Password_1234!'})
    assert res.status_code == 201, res.text
    return res.json()['token']


def headers(token):
    return {'Authorization': 'Bearer ' + token}


def test_scans_reports_and_exports_are_private_by_default(tmp_path):
    client=client_at(tmp_path)
    assert client.get('/api/auth/status').json()['configured'] is False
    assert client.get('/api/scans').status_code==401
    assert client.get('/api/scans/1/report.pdf').status_code==401
    assert client.post('/api/scans/demo').status_code==401
    assert client.get('/api/reports/scans.csv').status_code==401
    assert client.delete('/api/scans/1').status_code==401


def test_setup_owner_then_login_after_restart_and_no_second_registration(tmp_path):
    client=client_at(tmp_path)
    token=setup(client)
    assert client.get('/api/auth/me', headers=headers(token)).json()['username']=='farhan'
    assert client.get('/api/auth/status').json()['configured'] is True
    assert client.post('/api/auth/setup', json={'username':'another','password':'A_Strong_Password_1234!'}).status_code==409
    second=client_at(tmp_path)
    assert second.get('/api/auth/me', headers=headers(token)).status_code==200
    login=second.post('/api/auth/login', json={'username':'farhan', 'password':'A_Strong_Password_1234!'})
    assert login.status_code==200
    assert login.json()['token']!=token
    assert second.get('/api/scans',headers=headers(login.json()['token'])).status_code==200


def test_setup_requires_local_loopback_and_origin(tmp_path):
    remote=TestClient(create_app(db_path=str(tmp_path/'remote.sqlite')),base_url='http://external.example', client=('198.51.100.10',1234))
    assert remote.post('/api/auth/setup',json={'username':'farhan','password':'A_Strong_Password_1234!'}).status_code==403
    client=client_at(tmp_path)
    assert client.post('/api/auth/setup',json={'username':'farhan','password':'A_Strong_Password_1234!'},headers={'Origin':'https://evil.example'}).status_code==403
    assert client.get('/api/auth/status').json()['configured'] is False


def test_password_policy_and_auth_errors(tmp_path):
    client=client_at(tmp_path)
    assert client.post('/api/auth/setup',json={'username':'admin','password':'short'}).status_code==422
    setup(client)
    assert client.post('/api/auth/login',json={'username':'farhan','password':'wrong_wrong_123'}).status_code==401
    assert client.get('/api/auth/me',headers=headers('not_a_real_token')).status_code==401


def test_failed_logins_lock_out_account_and_correct_password_then_fails(tmp_path):
    client=client_at(tmp_path)
    setup(client)
    for _ in range(6):
        client.post('/api/auth/login',json={'username':'farhan','password':'wrong_wrong_123'})
    r=client.post('/api/auth/login',json={'username':'farhan','password':'A_Strong_Password_1234!'})
    assert r.status_code==429


def test_logout_revokes_bearer(tmp_path):
    client=client_at(tmp_path)
    token=setup(client)
    assert client.post('/api/auth/logout',headers=headers(token)).status_code==200
    assert client.get('/api/auth/me',headers=headers(token)).status_code==401


def test_password_change_invalidates_previous_sessions(tmp_path):
    client=client_at(tmp_path)
    token=setup(client)
    response=client.post('/api/auth/password',json={'current_password':'A_Strong_Password_1234!','new_password':'Even_Better_Password_1234!'}, headers=headers(token))
    assert response.status_code==200, response.text
    assert client.get('/api/auth/me',headers=headers(token)).status_code==401
    assert client.post('/api/auth/login',json={'username':'farhan','password':'A_Strong_Password_1234!'}).status_code==401
    assert client.post('/api/auth/login',json={'username':'farhan','password':'Even_Better_Password_1234!'}).status_code==200


def test_authorized_scans_delete_export_and_audit(tmp_path):
    client=client_at(tmp_path)
    token=setup(client)
    h=headers(token)
    assert client.get('/api/scans',headers=h).json()==[]
    saved=client.post('/api/scans/demo',headers=h).json()
    scanid=saved['id']
    assert client.get(f'/api/scans/{scanid}/report.pdf',headers=h).content.startswith(b'%PDF')
    csv=client.get('/api/reports/scans.csv',headers=h)
    assert csv.status_code==200 and csv.headers['content-type'].startswith('text/csv')
    assert b'scan_id,target' in csv.content
    assert b'demo.example' in csv.content or b'demo' in csv.content
    assert client.delete(f'/api/scans/{scanid}',headers=h).status_code==204
    assert client.get(f'/api/scans/{scanid}',headers=h).status_code==404
    assert client.delete(f'/api/scans/{scanid}',headers=h).status_code==404
    events=client.get('/api/audit',headers=h)
    assert events.status_code==200
    assert 'scan_deleted' in [e['action'] for e in events.json()]


def test_session_expiry_and_revocation_in_database(tmp_path):
    import hashlib,sqlite3
    client=client_at(tmp_path)
    token=setup(client)
    with sqlite3.connect(tmp_path/'workspace.sqlite') as db:
        db.execute('UPDATE sessions SET expires_at=0 WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))
    assert client.get('/api/auth/me',headers=headers(token)).status_code==401


def test_escaped_csv_disarms_spreadsheet_formula_inputs(tmp_path):
    import csv, io
    from app.exports import create_scan_csv
    rows=[{'id':4,'target':'=HYPERLINK("https://evil.invalid")','demo':True,'scanned_at':'2026-10-16T10:00:00Z','score':70,'findings':[]}]
    parsed=list(csv.DictReader(io.StringIO(create_scan_csv(rows))))
    assert parsed[0]['target'].startswith("'=")


def test_local_reset_revokes_old_sessions(tmp_path):
    from app.auth import AuthStore
    client=client_at(tmp_path)
    token=setup(client)
    AuthStore(str(tmp_path/'workspace.sqlite')).reset_password('Long_Replacement_Password_99')
    assert client.get('/api/auth/me',headers=headers(token)).status_code==401
    assert client.post('/api/auth/login',json={'username':'farhan','password':'Long_Replacement_Password_99'}).status_code==200
