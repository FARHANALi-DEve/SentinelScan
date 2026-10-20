from fastapi.testclient import TestClient
from app.main import create_app
from app.demo import demo_result


def build_client(tmp_path, allowed=''):
    return TestClient(create_app(db_path=str(tmp_path / 'scans.db'), allowed_hosts=allowed, require_auth=False))

def test_health_and_demo_scan_persist_across_app_restart(tmp_path):
    client=build_client(tmp_path)
    assert client.get('/api/health').json()['status']=='ok'
    response=client.post('/api/scans/demo')
    assert response.status_code==201
    scan=response.json()
    assert scan['demo'] is True and scan['score'] < 100 and scan['findings']
    again=build_client(tmp_path)
    found=again.get(f"/api/scans/{scan['id']}")
    assert found.status_code==200 and found.json()['id']==scan['id']
    assert again.get('/api/scans').json()[0]['id']==scan['id']

def test_report_is_downloadable_pdf(tmp_path):
    client=build_client(tmp_path)
    sid=client.post('/api/scans/demo').json()['id']
    pdf=client.get(f'/api/scans/{sid}/report.pdf')
    assert pdf.status_code==200
    assert pdf.headers['content-type']=='application/pdf'
    assert pdf.content.startswith(b'%PDF') and len(pdf.content)>1800

def test_default_host_allowlist_disables_live_scan(tmp_path):
    client=build_client(tmp_path)
    response=client.post('/api/scans',json={'target':'https://example.com'})
    assert response.status_code==422
    assert 'ALLOWED_TARGET_HOSTS' in response.json()['detail']
    assert client.get('/api/scans').json()==[]

def test_malformed_target_rejected(tmp_path):
    client=build_client(tmp_path,'example.com')
    response=client.post('/api/scans',json={'target':'http://127.0.0.1:8080/'})
    assert response.status_code==422

def test_valid_target_uses_scanner_and_persists(tmp_path,monkeypatch):
    import app.main as main
    called=[]
    def fake_scan(target,policy):
        called.append(target.hostname)
        return {**demo_result(),'target':target.url,'demo':False}
    monkeypatch.setattr(main,'scan_target',fake_scan)
    client=build_client(tmp_path,'example.com')
    resp=client.post('/api/scans',json={'target':'https://example.com'})
    assert resp.status_code==201 and called==['example.com']
    assert resp.json()['demo'] is False

def test_unknown_report_returns_404(tmp_path):
    assert build_client(tmp_path).get('/api/scans/999/report.pdf').status_code==404

def test_history_pagination_is_bounded(tmp_path):
    client=build_client(tmp_path)
    for _ in range(4): client.post('/api/scans/demo')
    assert len(client.get('/api/scans?limit=2').json())==2
    assert client.get('/api/scans?limit=999999').status_code==422
