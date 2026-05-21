---

#  Red Team Capstone Challenge — Team 4

##  Project Overview

This repository documents **Team 4’s completion of the TryHackMe Red Team Capstone Challenge**, a realistic multi-stage Active Directory simulation designed to replicate a real-world red team engagement.

The exercise simulates an end-to-end attack lifecycle, including reconnaissance, initial access, privilege escalation, lateral movement, Active Directory compromise, and structured reporting.

The goal of this project is to demonstrate practical offensive security skills, structured methodology, and professional cybersecurity documentation suitable for portfolio presentation.

---

##  Skills Demonstrated

* Active Directory attack methodology (Kerberoasting, DCSync concepts)
* Lateral movement and credential reuse analysis (Pass-the-Hash concepts)
* Windows security testing and post-exploitation workflows
* Network tunneling and pivoting concepts (SOCKS/Chisel usage)
* Privilege escalation in enterprise Windows environments
* Offensive security reporting and documentation
* Red team operational thinking and engagement flow

---

##  Lab Environment

* **Environment Type:** Simulated enterprise Active Directory network
* **Domain Structure:** Single forest with multiple organizational units (OUs)
* **Systems Included:** Domain Controllers, Windows endpoints, file servers, service accounts
* **Objective:** Multi-stage compromise simulating corporate-to-critical infrastructure access

---

##  Repository Structure

```
/writeup                → Detailed engagement documentation (HTML / DOCX)
/reports                → Final PDF reports and deliverables
/assets/screenshots    → Evidence and visual attack progression
/resources             → Supporting files and reference materials
/scripts               → Automation and helper scripts

README.md              → Project documentation
requirements.txt       → Python dependencies list
```

---

## Installation & Setup

This project includes optional Python-based automation and helper scripts used during the engagement.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/red-team-capstone.git
cd red-team-capstone
```

---

### 2️⃣ Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

Install all required Python libraries:

```bash
pip install -r requirements.txt
```

---

### What the Requirements Cover

The `requirements.txt` includes libraries commonly used for:

* Network requests and automation
* Active Directory interaction helpers
* Packet and traffic analysis support
* Credential handling and cryptography utilities
* Web and data parsing
* Scripting and automation support

---

## Automation Scripts Usage

All automation scripts are located in:

```
/scripts
```

### Purpose of Automation Scripts

These scripts are designed to assist with:

* Streamlining repetitive enumeration tasks
* Parsing and organizing collected data
* Assisting with report formatting and evidence collection
* Supporting workflow efficiency during lab execution

---

### How to Use Scripts

Run scripts individually depending on the task:

```bash
python scripts/<script_name>.py
```

---

### When to Use Automation Scripts

Use scripts in the following scenarios:

* During **initial enumeration** to organize scan outputs
* When processing **large output datasets** (e.g., scan results, logs)
* For **report generation support** (formatting / structuring evidence)
* During **post-exploitation documentation phases**

Do NOT use automation scripts blindly—review output and validate results manually as part of proper red team methodology.

---

## Attack Chain Summary

1. **Reconnaissance**
   Environment enumeration and surface discovery

2. **Initial Access**
   Entry via credential exposure and misconfigurations

3. **Credential Exploitation**
   Kerberoasting and credential validation workflows

4. **Lateral Movement**
   Pivoting between systems using valid credentials

5. **Active Directory Compromise**
   Domain-level privilege escalation concepts

6. **Persistence & Reporting**
   Maintaining simulated access and documenting findings

---

## Tools & Techniques

* Impacket
* PowerView
* Mimikatz
* Rubeus
* Evil-WinRM
* Chisel
* smbclient
* Hashcat
* Hydra
* Nmap
* ProxyChains

---

## Learning Outcomes

This project demonstrates:

* Realistic Active Directory attack chains
* Red team operational methodology
* Windows enterprise exploitation concepts
* Structured cybersecurity reporting
* Adaptation and problem-solving in multi-stage environments

---

## Credits

**Team 4 Contributors:**

* ABRAM NADY SHAFIQ (Lead)
* AYMAN AHMED SAEED
* AMR ADEL
* TARIQ HANI MUHAMMAD SAYED

**Instructor:** Ahmad Ashraf
**Platform:** TryHackMe Red Team Capstone Challenge

---
