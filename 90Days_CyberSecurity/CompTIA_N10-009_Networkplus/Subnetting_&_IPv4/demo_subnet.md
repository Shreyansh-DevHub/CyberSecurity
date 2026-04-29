# Subnetting & IPv4 Lab

## Scenario
A company has 3 departments: HR, IT, Sales. Each needs its own subnet.

## Steps
1. Base network: 192.168.10.0/24
2. Subnetting:
   - HR: /26 → 192.168.10.0–63
   - IT: /27 → 192.168.10.64–95
   - Sales: /28 → 192.168.10.96–111
3. Assign router interfaces:
   - HR → 192.168.10.1
   - IT → 192.168.10.65
   - Sales → 192.168.10.97
4. Verify with `ping` and `arp -a`.
