# 🛡️ Project 3: Network Security Lab

## 📌 Overview
This project focuses on basic network security controls in Windows, including:
- Configuring firewall rules to block specific traffic.
- Capturing and analyzing packets using Wireshark.
- Implementing strong password policies.

These steps demonstrate how layered security (defense in depth) protects systems from unauthorized access and network threats.

---

## 🧩 Objectives
- Create and test a custom firewall rule (Block ICMP).
- Capture network traffic before and after applying the rule.
- Configure password policies to enforce strong authentication.

---


2. Tools used:
- **Windows Defender Firewall**
- **Wireshark**
- **Local Security Policy (secpol.msc)**

---

## 🔒 Firewall Rule Demo
- Created a custom inbound rule named **Block_ICMP** to block ping (ICMP) traffic.
- Verified by running:

   "ping google.com"

