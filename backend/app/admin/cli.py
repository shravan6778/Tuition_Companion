"""Command-line administration, for the very first administrator (who has no dashboard yet) and for emergencies.

    python -m app.admin.cli pending                 teachers waiting for approval
    python -m app.admin.cli approve <username>      activate a teacher (put the username in ADMIN_USERNAMES to make them an admin)
    python -m app.admin.cli invite [--note TEXT] [--days N]    print a one-time teacher invite code

Each action is written to the audit log (actor "cli")."""
import argparse

from sqlalchemy import select

from app import audit
from app.auth import invites
from app.db.session import SessionLocal
from app.models import AccountStatus, Role, User


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.admin.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pending")
    p = sub.add_parser("approve")
    p.add_argument("username")
    p = sub.add_parser("invite")
    p.add_argument("--note", default=None)
    p.add_argument("--days", type=int, default=None, help="0 = never expires")
    args = ap.parse_args(argv)

    db = SessionLocal()
    try:
        if args.cmd == "pending":
            for u in db.scalars(select(User).where(User.status == AccountStatus.PENDING).order_by(User.created_at)):
                print(f"{u.username}\t{u.name}\t{u.role.value}\t{u.created_at:%Y-%m-%d}")
        elif args.cmd == "approve":
            user = db.scalar(select(User).where(User.username == args.username.strip().lower()))
            if user is None or user.status != AccountStatus.PENDING:
                print("No pending account with that username.")
                return 1
            user.status = AccountStatus.ACTIVE
            audit.record(db, "user.approve", target_type="user", target_id=user.id, target_label=user.username, detail={"by": "cli"})
            db.commit()
            print(f"{user.username} is active.")
        else:
            code, inv = invites.create_invite(db, None, args.note, args.days)
            audit.record(db, "invite.create", target_type="invite", target_id=inv.id, target_label=inv.note, detail={"by": "cli"})
            db.commit()
            print(f"Invite code (shown once): {code}")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
