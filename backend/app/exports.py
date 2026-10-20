"""Safe, spreadsheet-friendly CSV export of saved scans."""
import csv
import io


def safe_cell(value):
    text = str(value).replace('\x00','')
    # Excel/LibreOffice can interpret formulas even inside quoted CSV values.
    if text.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')) or text.startswith(('\t','\r','\n')):
        return "'" + text
    return text


def create_scan_csv(scans):
    stream=io.StringIO(newline='')
    writer=csv.writer(stream,lineterminator='\r\n')
    writer.writerow(['scan_id','target','scan_type','scanned_at','score','open_findings','passed_checks'])
    for scan in scans:
        findings=scan.get('findings',[])
        writer.writerow([scan['id'],safe_cell(scan['target']),'demo' if scan['demo'] else 'live',
                         safe_cell(scan['scanned_at']),scan['score'],sum(x['severity']!='pass' for x in findings),
                         sum(x['severity']=='pass' for x in findings)])
    return stream.getvalue()
