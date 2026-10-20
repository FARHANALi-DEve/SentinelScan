"""Cross-layer local workflows: no internet traffic required."""
from fastapi.testclient import TestClient
from app.main import create_app
from app.report import generate_pdf
from app.demo import demo_result
from app.storage import Storage


def test_demo_flow_saved_history_details_and_pdf(tmp_path):
    app=create_app(db_path=str(tmp_path/'e2e.sqlite'),allowed_hosts='',require_auth=False)
    with TestClient(app) as client:
        start=client.get('/api/health')
        assert start.status_code==200 and not start.json()['live_scans_enabled']
        saved=client.post('/api/scans/demo').json()
        assert saved['id'] > 0
        assert saved['demo'] is True
        assert saved['findings'] and 0<=saved['score']<=100
        assert client.get('/api/scans').json()[0]['id']==saved['id']
        assert client.get(f"/api/scans/{saved['id']}").json()['findings']==saved['findings']
        pdf=client.get(f"/api/scans/{saved['id']}/report.pdf")
        assert pdf.content.startswith(b'%PDF')
        assert b'Acme' not in pdf.content  # compressed PDF should not leak browser demo tokens
        assert client.post('/api/scans',json={'target':'http://127.0.0.1'}).status_code==422
    assert Storage(str(tmp_path/'e2e.sqlite')).get(saved['id']) is not None


def test_many_findings_generate_multipage_pdf(tmp_path):
    doc=demo_result()
    doc['findings']=doc['findings']*8
    scan=Storage(str(tmp_path/'many.sqlite')).create(doc)
    pdf=generate_pdf(scan)
    assert pdf.startswith(b'%PDF') and len(pdf)>4500
