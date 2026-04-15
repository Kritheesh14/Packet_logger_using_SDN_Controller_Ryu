# SDN Live Packet Logger & Dashboard

A full-stack Software Defined Networking (SDN) application that provides a real-time web interface to monitor network traffic, protocol distribution, and packet logs. This project utilizes the **Ryu Controller** to manage a virtual network environment created with **Mininet**.

---

## Introduction
This project bridges the gap between low-level network control and high-level visualization. By capturing `PacketIn` events at the controller level, the application parses protocol data (TCP, UDP, ICMP, ARP) and exposes it via a REST API to a modern, dark-themed web dashboard.

## Key Challenges & Solutions
Developing with the Ryu framework on modern systems presents significant compatibility hurdles:

* **Problem:** Ryu 4.34 is fundamentally incompatible with modern `setuptools` (breaking during metadata generation) and newer `eventlet` versions (missing `ALREADY_HANDLED`).
* **Solution:** Implemented a **"Pinned Dependency" strategy**. By forcing `setuptools==58.0.0` and using the `--no-build-isolation` flag during installation, we bypass metadata corruption. Additionally, `eventlet` and `greenlet` are pinned to specific legacy versions to ensure runtime stability.

---

## Repository Structure
```text
.
├── controller/
│   └── p_log.py          # Ryu Controller & REST API logic
├── dashboard/
│   └── index.html        # Live Monitoring UI (HTML5/JavaScript)
├── requirements.txt      # Pinned dependencies for environment stability
└── README.md             # Project documentation
```

## Installation Guide

### 1. Prerequisites
Ensure you have Python 3.9 and Mininet installed on your system (WSL2 Ubuntu 22.04+ recommended).

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/ryu-packet-logger.git
cd ryu-packet-logger

# Create a fresh virtual environment
python3.9 -m venv ryu-vm
source ryu-vm/bin/activate

# Install core build tools first to prevent metadata errors
pip install "setuptools==58.0.0" "wheel==0.40.0" "pip<24.1"

# Install requirements using NO build isolation
pip install --no-build-isolation -r requirements.txt
```

Markdown

## Usage

### Step 1: Start the Controller
In your first terminal (with the `venv` activated):

```bash
ryu-manager controller/p_log.py
```

The API will start at: ``` http://127.0.0.1:8080/stats ```

### Step 2: Start the Topology

In a second terminal, launch the Mininet environment:
```
Bash

sudo mn --controller=remote,ip=127.0.0.1 --topo=linear,3 --switch=ovs,protocols=OpenFlow13
```

### Step 3: View Dashboard

Open dashboard/index.html in any modern web browser to see the live traffic charts and logs.


## Testing Traffic

To see the dashboard in action, run the following in the Mininet CLI:

```

pingall
# Observe ICMP and ARP spikes

h1 iperf -c h2
# Observe TCP traffic generation

h1 iperf -u -c h2 -b 1M
# Observe UDP stream monitoring

```
