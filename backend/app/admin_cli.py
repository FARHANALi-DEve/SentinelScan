"""Interactive, local-only password recovery. Never passes credentials via CLI flags."""
import getpass
import os
from pathlib import Path
from dotenv import load_dotenv
from .auth import AuthStore, AuthenticationError


def main():
    load_dotenv(Path(__file__).resolve().parents[2] / '.env')
    path=os.getenv('DATABASE_PATH',str(Path(__file__).resolve().parents[1]/'sentinelscan.db'))
    store=AuthStore(path)
    if not store.configured():
        print('No owner is configured yet. Use the website setup page first.')
        return 1
    print('LOCAL OWNER PASSWORD RESET — requires direct access to your SQLite database.')
    answer=input('Type RESET to revoke all sessions and change the password: ')
    if answer != 'RESET':
        print('Cancelled.')
        return 1
    new=getpass.getpass('New password (12–128 characters): ')
    confirmation=getpass.getpass('Confirm password: ')
    if new != confirmation:
        print('Passwords do not match.')
        return 1
    try:
        store.reset_password(new)
    except (ValueError,AuthenticationError) as exc:
        print(str(exc))
        return 1
    print('Password reset complete. All sessions are revoked. Sign in again.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
