# 🛠️ Detailed Setup & Installation Guide

This guide covers the exact steps required to set up a stable environment for the Ryu Controller and Mininet on modern Linux distributions (Ubuntu 22.04+ / WSL2). 

> **Note:** Ryu is a legacy framework. Following these steps precisely is critical to avoid `setuptools` and `eventlet` compatibility errors.

---

## 1. System Dependencies
Before setting up the Python environment, install the necessary system libraries for building Ryu's dependencies:

```bash
sudo apt-get update
sudo apt-get install -y gcc python3-dev libxml2-dev libxslt1-dev zlib1g-dev \
                        software-properties-common curl git
```
## 2. Python 3.9 Installation

Ryu is most stable on Python 3.9. If you are on a newer Ubuntu version, add the deadsnakes PPA:

```bash

sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev
```
## 3. Creating the Virtual Environment

We must "pin" specific versions of build tools to prevent pip from pulling in modern, incompatible versions during the build process.
```bash

# Create the environment
python3.9 -m venv ~/ryu-vm
source ~/ryu-vm/bin/activate

# Step A: Install specific legacy versions of installer tools
pip install "setuptools==58.0.0" "wheel==0.40.0" "pip<24.1"

# Step B: Install Ryu with NO build isolation
# This forces the installer to use our pinned setuptools instead of a fresh one
pip install --no-build-isolation ryu==4.34

# Step C: Fix the 'ALREADY_HANDLED' Eventlet error
pip install "eventlet==0.30.2" "greenlet==1.1.3"

# Step D: Install Dashboard dependencies
pip install WebOb werkzeug
```

## 4. Verification

Verify the installation by checking the version. If you see a Traceback error here, repeat Step 3.
```bash

ryu-manager --version
# Expected Output: ryu-manager 4.34
```

## 5. Running the Project

### Terminal 1: The Controller

Navigate to the project root and start the application:
```bash

source ~/ryu-vm/bin/activate
ryu-manager controller/p_log.py
```

### Terminal 2: The Network (Mininet)

In a separate terminal, launch the topology:
```bash

sudo mn --controller=remote,ip=127.0.0.1 --topo=linear,3 --switch=ovs,protocols=OpenFlow13
```

### Terminal 3: Traffic Generation

Inside the Mininet CLI (mininet>), run:
```bash

mininet> pingall
```

## Troubleshooting Common Issues

| Error                                      | Cause                   | Fix                                                     |
|-------------------------------------------|-------------------------|----------------------------------------------------------|
| AttributeError: ... get_script_args         | Modern setuptools       | Run `pip install setuptools==58.0.0` inside venv        |
| ImportError: ALREADY_HANDLED               | Modern eventlet         | Run `pip install eventlet==0.30.2`                      |
| Address already in use                    | Old session hanging     | Run `sudo mn -c` and `fuser -k 8080/tcp`                |


---

### How to add this to your Repo:
1.  **Create the file:** `nano SETUP.md`
2.  **Paste the code** above and save.
3.  **Link it in your README:** In your `README.md`, you can add a line like this:
    `For a detailed, step-by-step installation guide, see [SETUP.md](./SETUP.md).`

This setup is very professional and shows that you understand the **DevOps/Environment** side of software engineering, not just the coding side!
