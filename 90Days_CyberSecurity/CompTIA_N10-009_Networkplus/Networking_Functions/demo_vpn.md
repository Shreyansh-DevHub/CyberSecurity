# VPN Demo

## Objective
Establish a secure tunnel between two virtual machines.

## Steps
1. Install OpenVPN on both VMs.
2. Configure server with 10.8.0.1/24 subnet.
3. Connect client to server using .ovpn profile.

## Verification
- Client can ping server through VPN tunnel.
- Traffic is encrypted (verified with Wireshark).
