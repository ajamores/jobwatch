"""Email the new postings in new.json. Sends nothing when there is nothing new.

Needs two lines in .env (gitignored):

    GMAIL_USER=you@gmail.com
    GMAIL_APP_PASSWORD=abcdefghijklmnop     # 16 chars, no spaces

An app password is not your Google password — make one at
https://myaccount.google.com/apppasswords (requires 2FA on the account).

    python -m jobwatch.notify [data/new.json] [--to someone@else.com] [--always] [--dry-run]
"""

import argparse
import json
import os
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage
from html import escape
from pathlib import Path

from dotenv import load_dotenv

from .paths import DATA, ROOT


def age(j):
    """Not every board prints a posting date; say so rather than inventing one."""
    return f"posted {j['age_days']}d ago" if j.get("age_days") is not None else "date not listed"


def row(j):
    salary = j["salary"]["text"] or "—"
    tech = ", ".join((j["tech"] or [])[:6])
    meta = " · ".join(x for x in (
        j["workplace_type"], j["seniority"],
        f"{j['yoe']}+ yrs" if j["yoe"] else None,
    ) if x)
    return f"""
    <tr>
      <td style="padding:14px 0;border-bottom:1px solid #e5e5e5">
        <div style="font-size:15px;font-weight:600">
          <a href="{escape(j['apply_url'] or '#')}"
             style="color:#0b57d0;text-decoration:none">{escape(j['title'] or 'Untitled')}</a>
        </div>
        <div style="font-size:13px;color:#333;margin-top:2px">
          {escape(j['company'] or '')} — {escape(j['location'] or '')}
        </div>
        <div style="font-size:13px;color:#666;margin-top:4px">
          <strong>{escape(salary)}</strong>{' · ' + escape(meta) if meta else ''}
          · {escape(age(j))}
        </div>
        {f'<div style="font-size:12px;color:#888;margin-top:4px">{escape(tech)}</div>' if tech else ''}
      </td>
    </tr>"""


def build(jobs, label="hiring.cafe"):
    when = datetime.now().strftime("%a %-d %b, %-I:%M%p")
    html = f"""<html><body style="margin:0;padding:20px;background:#fafafa;
      font-family:-apple-system,Segoe UI,Roboto,sans-serif">
      <div style="max-width:640px;margin:0 auto;background:#fff;padding:24px;
                  border:1px solid #e5e5e5;border-radius:8px">
        <div style="font-size:18px;font-weight:600">
          {len(jobs)} new posting{'s' if len(jobs) != 1 else ''}</div>
        <div style="font-size:12px;color:#888;margin-bottom:8px">{escape(label)} · {when}</div>
        <table style="width:100%;border-collapse:collapse">{''.join(row(j) for j in jobs)}</table>
      </div></body></html>"""

    text = "\n\n".join(
        f"{j['title']} — {j['company']}\n{j['location']} · {j['salary']['text'] or '—'} "
        f"· {age(j)}\n{j['apply_url']}"
        for j in jobs
    )
    return html, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("new", nargs="?", default=str(DATA / "new.json"))
    ap.add_argument("--to")
    ap.add_argument("--label", default="hiring.cafe",
                    help="what to print under the heading")
    ap.add_argument("--always", action="store_true", help="send even when nothing is new")
    ap.add_argument("--dry-run", action="store_true", help="print, do not send")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    jobs = json.loads(Path(args.new).read_text())
    if not jobs and not args.always:
        print("nothing new, no email sent")
        return

    html, text = build(jobs, args.label)
    if args.dry_run:
        print(text or "(nothing new)")
        return
    if not user or not password:
        sys.exit("set GMAIL_USER and GMAIL_APP_PASSWORD in .env — see the docstring")

    msg = EmailMessage()
    msg["Subject"] = (f"{len(jobs)} new dev job{'s' if len(jobs) != 1 else ''}"
                      f" — {', '.join(dict.fromkeys(j['company'] for j in jobs))[:60]}"
                      if jobs else "No new dev jobs")
    msg["From"] = user
    msg["To"] = args.to or user
    msg.set_content(text or "Nothing new.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    print(f"emailed {len(jobs)} jobs to {msg['To']}")


if __name__ == "__main__":
    main()
