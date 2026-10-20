"""SentinelScan local-first API: authenticated owner, private scans and exports."""
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from .auth import AuthStore, AuthenticationError, AccountLocked
from .exports import create_scan_csv
from .policy import TargetPolicy, PolicyError
from .scanner import scan_target
from .demo import demo_result
from .storage import Storage
from .report import generate_pdf

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

class ScanRequest(BaseModel):
    target: str = Field(min_length=1,max_length=2048)

class Credentials(BaseModel):
    username: str=Field(min_length=3,max_length=30)
    password: str=Field(min_length=1,max_length=128)

class PasswordChange(BaseModel):
    current_password: str=Field(min_length=1,max_length=128)
    new_password: str=Field(min_length=12,max_length=128)


def create_app(db_path=None, allowed_hosts=None, require_auth=True):
    if allowed_hosts is None:
        allowed_hosts=os.getenv('ALLOWED_TARGET_HOSTS','')
    if isinstance(allowed_hosts,str):
        allowed_hosts=[x.strip() for x in allowed_hosts.split(',') if x.strip()]
    policy=TargetPolicy(allowed_hosts)
    db_path=db_path or os.getenv('DATABASE_PATH',str(Path(__file__).resolve().parents[1] / 'sentinelscan.db'))
    store=Storage(str(db_path))
    auth=AuthStore(str(db_path))
    app=FastAPI(title='SentinelScan API',version='2.0.0',description='Private, authorized, passive website posture checks.')
    origins=[x.strip().rstrip('/') for x in os.getenv('FRONTEND_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET','POST','DELETE'],allow_headers=['Content-Type','Authorization'])

    def require_owner(authorization: str | None = Header(None)):
        if not require_auth:
            return 'test-owner'
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401,detail='Sign in to access this workspace')
        user=auth.user_for(authorization[7:])
        if not user:
            raise HTTPException(status_code=401,detail='Session expired. Please sign in again.')
        return user

    @app.get('/api/health')
    def health():
        return {'status':'ok','service':'SentinelScan','version':'2.0.0','live_scans_enabled':bool(policy.allowed_hosts)}

    @app.get('/api/auth/status')
    def auth_status():
        return {'configured':auth.configured()}

    @app.post('/api/auth/setup',status_code=201)
    def setup(credentials:Credentials,request:Request):
        # First-run registration is permitted from local API clients only. Never accept
        # public internet registration when exposed behind a remote reverse proxy.
        if not request.client or request.client.host not in {'127.0.0.1','::1','testclient'}:
            raise HTTPException(status_code=403,detail='First-time setup is local-only')
        origin=request.headers.get('origin')
        if origin and origin.rstrip('/') not in origins:
            raise HTTPException(status_code=403,detail='Untrusted setup origin')
        try:
            token=auth.create_owner(credentials.username,credentials.password)
        except ValueError as e:
            raise HTTPException(status_code=422,detail=str(e)) from e
        except AuthenticationError as e:
            raise HTTPException(status_code=409,detail=str(e)) from e
        return {'token':token,'username':credentials.username}

    @app.post('/api/auth/login')
    def login(credentials:Credentials):
        try:
            token=auth.login(credentials.username,credentials.password)
        except AccountLocked as e:
            raise HTTPException(status_code=429,detail=str(e),headers={'Retry-After':'900'}) from e
        except AuthenticationError as e:
            raise HTTPException(status_code=401,detail=str(e)) from e
        return {'token':token,'username':credentials.username}

    @app.get('/api/auth/me')
    def me(username:str=Depends(require_owner)):
        return {'username':username,'role':'owner'}

    @app.post('/api/auth/logout')
    def logout(authorization:str=Header(''),username:str=Depends(require_owner)):
        if require_auth:
            auth.logout(authorization[7:])
        return {'ok':True}

    @app.post('/api/auth/password')
    def password(body:PasswordChange,username:str=Depends(require_owner)):
        try:
            auth.change_password(body.current_password,body.new_password)
        except AuthenticationError as e:
            raise HTTPException(status_code=401,detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=422,detail=str(e)) from e
        return {'ok':True,'sessions_revoked':True}

    @app.post('/api/scans/demo',status_code=201)
    def create_demo_scan(username:str=Depends(require_owner)):
        result=store.create(demo_result())
        auth.log('demo_scan',f'Assessment #{result["id"]}')
        return result

    @app.post('/api/scans',status_code=201)
    def create_live_scan(body:ScanRequest,username:str=Depends(require_owner)):
        try:
            target=policy.validate(body.target)
        except PolicyError as exc:
            raise HTTPException(status_code=422,detail=str(exc)) from exc
        result=store.create(scan_target(target,policy))
        auth.log('live_scan',f'Assessment #{result["id"]}')
        return result

    @app.get('/api/scans')
    def list_scans(limit:int=Query(50,ge=1,le=200),username:str=Depends(require_owner)):
        return store.list(limit)

    @app.get('/api/scans/{scan_id}')
    def get_scan(scan_id:int,username:str=Depends(require_owner)):
        data=store.get(scan_id)
        if not data:
            raise HTTPException(status_code=404,detail='Scan not found')
        return data

    @app.delete('/api/scans/{scan_id}',status_code=204)
    def delete_scan(scan_id:int,username:str=Depends(require_owner)):
        if not store.delete(scan_id):
            raise HTTPException(status_code=404,detail='Scan not found')
        auth.log('scan_deleted',f'Assessment #{scan_id}')
        return Response(status_code=204)

    @app.get('/api/scans/{scan_id}/report.pdf')
    def report(scan_id:int,username:str=Depends(require_owner)):
        data=store.get(scan_id)
        if not data:
            raise HTTPException(status_code=404,detail='Scan not found')
        return Response(content=generate_pdf(data),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="sentinelscan-report-{scan_id}.pdf"','Cache-Control':'no-store'})

    @app.get('/api/reports/scans.csv')
    def csv_export(username:str=Depends(require_owner)):
        return Response(content=create_scan_csv(store.list(200)),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="sentinelscan-scans.csv"','Cache-Control':'no-store'})

    @app.get('/api/audit')
    def audit_events(limit:int=Query(50,ge=1,le=100),username:str=Depends(require_owner)):
        return auth.events(limit)

    return app

app=create_app()
