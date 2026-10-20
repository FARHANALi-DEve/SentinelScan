"""Printable local PDF reports generated exclusively from saved scan data."""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

INK=HexColor('#0b172c')
ACCENT=HexColor('#0c999f')
MUTED=HexColor('#52647a')


def generate_pdf(scan:dict)->bytes:
    stream=BytesIO()
    page=canvas.Canvas(stream,pagesize=(595,842))
    page.setTitle(f"SentinelScan Report #{scan['id']}")
    y=0
    def new_page():
        nonlocal y
        page.setFillColor(INK); page.rect(0,0,595,842,fill=1,stroke=0)
        page.setFillColor(ACCENT); page.rect(44,792,3,28,fill=1,stroke=0)
        page.setFont('Helvetica-Bold',19);page.setFillColorRGB(1,1,1)
        page.drawString(57,799,'SENTINELSCAN')
        page.setFont('Helvetica',9);page.setFillColor(HexColor('#a6c6d2'))
        page.drawRightString(551,806,'SECURITY POSTURE REPORT')
        page.setStrokeColor(HexColor('#2b3c51')); page.line(43,777,552,777)
        y=756
    def line(text, size=10, color=None, bold=False, width=500, leading=15):
        nonlocal y
        if color is None:color=HexColor('#e3edf7')
        font='Helvetica-Bold' if bold else 'Helvetica'
        # ASCII normalization avoids built-in PDF font Unicode loss and escaping problems.
        text=str(text).encode('latin-1','replace').decode('latin-1')
        rows=simpleSplit(text,font,size,width) or ['']
        for row in rows:
            if y<68:
                page.showPage();new_page()
            page.setFont(font,size);page.setFillColor(color);page.drawString(45,y,row)
            y-=leading
    new_page()
    line('WEBSITE ASSESSMENT',11,ACCENT,True,leading=24)
    line(scan.get('target','unknown'),14,bold=True,leading=22)
    line(f"Scan ID: {scan['id']}      Scanned: {scan.get('scanned_at','')}      {'OFFLINE DEMO' if scan.get('demo') else 'AUTHORIZED LIVE SCAN'}",9,MUTED,leading=28)
    line(f"POSTURE SCORE   {scan.get('score',0)} / 100",20,HexColor('#61ded2'),True,leading=31)
    line('Configuration indicators only — NOT a penetration test or a security guarantee.',9,HexColor('#e7bb7a'),leading=32)
    for idx,item in enumerate(scan.get('findings',[]),1):
        if y<170:
            page.showPage();new_page()
        line(f"{idx:02d}   {item['title']}    [{item['severity'].upper()}]",11,HexColor('#78dbd5') if item['severity']=='pass' else HexColor('#ffba8b'),True,leading=19)
        line(item.get('description',''),9,leading=14)
        line('Evidence: '+item.get('evidence',''),9,HexColor('#9eb0c9'),leading=14)
        line('Recommendation: '+item.get('recommendation',''),9,HexColor('#d1ecff'),leading=22)
    if y<80:
        page.showPage();new_page()
    line('SentinelScan checks passive HTTP/TLS configuration indicators only.',9,HexColor('#9eb0c9'))
    line('Only scan assets you own or have permission to assess.',9,HexColor('#9eb0c9'))
    page.save()
    return stream.getvalue()
