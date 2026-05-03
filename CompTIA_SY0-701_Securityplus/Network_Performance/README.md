# Project 6: Network Performance Optimization Lab

## Overview
This project was done on Kali Linux to measure and optimize network performance.  
The goal was to learn how to check bandwidth, latency, and network paths using tools like iperf3, ping, and traceroute.  
It also included testing different conditions (wired vs wireless, firewall enabled vs disabled) to see how performance changes.

---

## Steps

### 1. Bandwidth Test with iperf3
- Started iperf3 in server mode:
  ```bash
  iperf3 -s

Ran iperf3 client from another terminal:
iperf3 -c <server_ip>

### 2. Latency Test with Ping
traceroute 8.8.8.8
