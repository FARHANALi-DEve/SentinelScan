"""Simple transactional SQLite history for local-only scanner operation."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class Storage:
    def __init__(self, path: str):
        self.path=path
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanned_at TEXT NOT NULL,
                target TEXT NOT NULL,
                demo INTEGER NOT NULL,
                payload TEXT NOT NULL
            )''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_scans_scanned_at ON scans (scanned_at DESC)')

    def _connect(self):
        connection=sqlite3.connect(self.path, timeout=10)
        connection.execute('PRAGMA busy_timeout=10000')
        return connection

    def create(self, result:dict)->dict:
        document={**result,'scanned_at':result.get('scanned_at') or datetime.now(timezone.utc).isoformat()}
        data=json.dumps(document,ensure_ascii=True,allow_nan=False)
        with self._connect() as db:
            cursor=db.execute('INSERT INTO scans (scanned_at,target,demo,payload) VALUES (?,?,?,?)',
                              (document['scanned_at'],document['target'],int(bool(document['demo'])),data))
            document['id']=cursor.lastrowid
        return document

    def get(self,scan_id:int):
        with self._connect() as db:
            row=db.execute('SELECT id,payload FROM scans WHERE id=?',(scan_id,)).fetchone()
        return {**json.loads(row[1]),'id':row[0]} if row else None

    def list(self,limit:int=50):
        with self._connect() as db:
            rows=db.execute('SELECT id,payload FROM scans ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [{**json.loads(r[1]),'id':r[0]} for r in rows]

    def delete(self, scan_id:int)->bool:
        with self._connect() as db:
            result = db.execute('DELETE FROM scans WHERE id=?', (scan_id,))
            return result.rowcount > 0
