# Red Team Capstone Challenge — Team 4

## Project Overview
This repository contains the Team 4 deliverables for the Red Team Capstone Challenge (TryHackMe). It documents a simulated Active Directory engagement with attack chain, tooling, artifacts, and final reporting suitable for recruiter portfolios.

## Skills Covered
- Active Directory Exploitation (Kerberoasting, DCSync)
- Lateral Movement, Pass-the-Hash, Pivoting
- Chisel tunneling and proxying
- Golden Ticket concepts and persistence
- Report generation and post-engagement documentation

## Lab Overview
- Domains: simulated AD domain(s)
- Forest structure: single forest with multiple OUs (documented in writeup)
- Environment: Windows domain controllers, endpoints, file shares, and service accounts

## Attack Chain Summary
1. Reconnaissance
2. Initial access and credential harvesting
3. Kerberoasting and credential cracking
4. Lateral movement and DCSync
5. Persistence and reporting

## Tools Used
- Impacket, PowerView (PowerShell)
- Mimikatz, Rubeus
- Chisel (tunneling)
- Evil-WinRM, smbclient
- Hashcat, Hydra
- Nmap, ProxyChains

## Repository Structure
- /writeup — HTML/DOCX walkthroughs and step-by-step notes
- /reports — PDF reports and deliverables
- /assets — screenshots and images (see screenshots folder)
- /resources — supporting archives and helper files
- /scripts — automation and helper scripts
- README.md, requirements.txt — top-level documentation

## Screenshots
Screenshots referenced in the writeup are in /assets/screenshots

## Learning Outcomes
This project demonstrates AD offensive tradecraft, tooling, and professional reporting suitable for portfolio presentation.

## Credits
- Team 4: Lamona (lead), contributors
- Instructor and TryHackMe materials

## Disclaimer
For educational and authorized lab use only. Do not run these techniques against systems without explicit authorization.
# refresh
