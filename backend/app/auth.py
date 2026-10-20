"""Single-owner account and revocable local sessions. No shared default credentials."""
import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from pathlib import Path

PASSWORD_MIN_LENGTH = 12
SESSION_LIFETIME_SECONDS = 8 * 3600


class AuthenticationError(Exception):
    pass


class AccountLocked(AuthenticationError):
    pass


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    value = hashlib.scrypt(password.encode('utf8'), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return salt.hex() + '$' + value.hex()


def matches_password(password, stored):
    try:
        salt, expected = stored.split('$',1)
        actual = hash_password(password, bytes.fromhex(salt)).split('$',1)[1]
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, OverflowError):
        return False


def enforce_password(password):
    if not (PASSWORD_MIN_LENGTH <= len(password) <= 128):
        raise ValueError('Use a password between 12 and 128 characters.')


def fingerprint(token):
    return hashlib.sha256(token.encode()).hexdigest()


class AuthStore:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self._db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS owner_account (
                id INTEGER PRIMARY KEY CHECK (id=1), username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL, failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until REAL NOT NULL DEFAULT 0)''')
            db.execute('''CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY, owner_id INTEGER NOT NULL,
                expires_at REAL NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, created_at REAL NOT NULL,
                action TEXT NOT NULL, details TEXT NOT NULL DEFAULT '')''')

    def _db(self):
        db = sqlite3.connect(self.path,timeout=10)
        db.execute('PRAGMA busy_timeout=10000')
        return db

    def configured(self):
        with self._db() as db:
            return db.execute('SELECT 1 FROM owner_account WHERE id=1').fetchone() is not None

    def create_owner(self, username, password):
        if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_.-]{2,29}',username):
            raise ValueError('Username must be 3–30 characters and start with a letter.')
        enforce_password(password)
        password_hash = hash_password(password)
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM owner_account WHERE id=1').fetchone():
                raise AuthenticationError('Owner already exists')
            db.execute('INSERT INTO owner_account(id,username,password_hash) VALUES (1,?,?)', (username,password_hash))
            self._log(db,'account_created','First owner initialized')
            return self._issue(db)

    def _issue(self, db):
        token=secrets.token_urlsafe(40)
        db.execute('INSERT INTO sessions(token_hash,owner_id,expires_at) VALUES (?,1,?)', (fingerprint(token),time.time()+SESSION_LIFETIME_SECONDS))
        return token

    def login(self,username,password):
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT username,password_hash,failed_attempts,locked_until FROM owner_account WHERE id=1').fetchone()
            if row is None or row[0] != username:
                raise AuthenticationError('Invalid username or password')
            if row[3] > time.time():
                raise AccountLocked('Too many failed attempts. Try again in 15 minutes.')
            if not matches_password(password,row[1]):
                attempts=row[2]+1
                until=time.time()+900 if attempts>=6 else 0
                db.execute('UPDATE owner_account SET failed_attempts=?,locked_until=? WHERE id=1',(attempts,until))
                self._log(db,'login_failed','Incorrect credentials')
                # Need to commit lockout state before raising.
                db.commit()
                raise AuthenticationError('Invalid username or password')
            db.execute('UPDATE owner_account SET failed_attempts=0,locked_until=0 WHERE id=1')
            token=self._issue(db)
            self._log(db,'login','Signed in')
            return token

    def user_for(self,token):
        if not token or len(token)>256:
            return None
        with self._db() as db:
            row=db.execute('''SELECT u.username FROM sessions s
                JOIN owner_account u ON u.id=s.owner_id
                WHERE s.token_hash=? AND s.expires_at>?''',(fingerprint(token),time.time())).fetchone()
        return row[0] if row else None

    def logout(self,token):
        with self._db() as db:
            db.execute('DELETE FROM sessions WHERE token_hash=?',(fingerprint(token),))
            self._log(db,'logout','Signed out')

    def change_password(self,current,new):
        enforce_password(new)
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            stored=db.execute('SELECT password_hash FROM owner_account WHERE id=1').fetchone()
            if not stored or not matches_password(current,stored[0]):
                raise AuthenticationError('Current password is incorrect')
            db.execute('UPDATE owner_account SET password_hash=?,failed_attempts=0,locked_until=0 WHERE id=1',(hash_password(new),))
            db.execute('DELETE FROM sessions')
            self._log(db,'password_changed','Credentials updated; sessions revoked')

    def reset_password(self, new):
        """Local administrator recovery; never exposed as a web endpoint."""
        enforce_password(new)
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM owner_account WHERE id=1').fetchone():
                raise AuthenticationError('Owner not configured')
            db.execute('UPDATE owner_account SET password_hash=?,failed_attempts=0,locked_until=0 WHERE id=1', (hash_password(new),))
            db.execute('DELETE FROM sessions')
            self._log(db,'password_reset','Local administrator reset; sessions revoked')

    def reset_password(self,new_password):
        """Local machine recovery tool only; requires direct database file access."""
        enforce_password(new_password)
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM owner_account WHERE id=1').fetchone():
                raise AuthenticationError('No owner account has been created')
            db.execute('UPDATE owner_account SET password_hash=?,failed_attempts=0,locked_until=0 WHERE id=1', (hash_password(new_password),))
            db.execute('DELETE FROM sessions')
            self._log(db,'password_reset','Owner credentials reset locally')

    def log(self,action,details=''):
        with self._db() as db:
            self._log(db,action,details)

    def _log(self,db,action,details=''):
        db.execute('INSERT INTO audit_events(created_at,action,details) VALUES (?,?,?)',(time.time(),action,str(details)[:150]))

    def events(self,limit=50):
        with self._db() as db:
            data=db.execute('SELECT id,created_at,action,details FROM audit_events ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        return [{'id':r[0],'created_at':r[1],'action':r[2],'details':r[3]} for r in data]
