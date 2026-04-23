# Running the SDN Stack

Follow these steps exactly to orchestrate the Controller, the Network, and the Dashboard. 

---

## 1. Prepare Your Workspace
Before starting, ensure you have no "ghost" processes running from previous sessions:
```bash
# Clear any stuck Mininet topologies and kill processes on port 8080
sudo mn -c
sudo fuser -k 8080/tcp
````

-----

## 2\. Terminal 1: The Ryu Controller (The Brain)

This terminal handles the logic and hosts the REST API.

1.  **Navigate to the Project Root:**
    ```bash
    cd ~/ryu-project
    ```
2.  **Activate the Environment:**
    ```bash
    source ~/ryu-vm/bin/activate
    ```
3.  **Launch the Controller:**
    ```bash
    ryu-manager controller/p_log.py
    ```

*Verification: You should see "WSGI starting up on https://www.google.com/search?q=http://0.0.0.0:8080".*

-----

## 3\. Terminal 2: Mininet (The Network)

This terminal creates the virtual hardware.

1.  **Open a new Terminal tab/window.**
2.  **Execute the Mininet Command:**
    ```bash
    sudo mn --controller=remote,ip=127.0.0.1 --topo=linear,3 --switch=ovs,protocols=OpenFlow13
    ```

*Verification: The `mininet>` prompt appears, and Terminal 1 should log "Switch connected".*

-----

## 4\. Terminal 3: The Dashboard (The View)

1.  **Locate the file:** `~/ryu-project/dashboard/index.html`.
2.  **Open in Windows:**
    ```bash
    # Type this in WSL to open the folder in Windows
    explorer.exe dashboard
    ```
3.  **Launch:** Double-click `index.html` to open it in Chrome/Edge.

-----

## 5\. Stress Testing: Surging Protocol Values

To demonstrate the responsiveness of the graphs, use the following commands in the **Mininet CLI (Terminal 2)**.

### A. Surge ICMP (Ping Traffic)

Generates spikes in the **Purple** bar.

```bash
mininet> pingall
# Or for a continuous surge:
mininet> h1 ping h3
```

### B. Surge TCP (Bandwidth Stress)

Generates spikes in the **Teal** bar. Simulates a high-speed file transfer.

```bash
# Run a 10-second TCP bandwidth test between Host 1 and Host 3
mininet> h1 iperf -c h3 -t 10
```

### C. Surge UDP (Stream Stress)

Generates spikes in the **Coral/Red** bar. Simulates a 5Mbps video stream.

```bash
# Run a 10-second UDP stream at 5 Megabits per second
mininet> h1 iperf -u -c h2 -b 5M -t 10
```
In case connection isnt established, run :
```bash
h3 iperf -s &
```
-----


## Obtaining Flow tables
Considering both the terminals are open [controller and emulator, where controller is running the _p_log.py_ file and the emulator is running mininet], run this in the 3rd terminal : 

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

If you want to capture a live view, run this in another terminal :
```bash
watch -n 1 "sudo ovs-ofctl -O OpenFlow13 dump-flows s1"
```

---

## How to Properly Shutdown

1.  **Mininet:** Type `exit` in Terminal 2.
2.  **Ryu:** Press `Ctrl + C` in Terminal 1.
3.  **Clean:** Run `sudo mn -c` to ensure the virtual switches are deleted from the kernel.

<!-- end list -->

```

### Why this structure works:
* **Terminal 1** is your **Control Plane**.
* **Terminal 2** is your **Data Plane**.
* **The Dashboard** is your **Application Plane**. 

By running these in order, you are following the proper initialization sequence of a Software Defined Network. If you follow these steps, your dashboard will reflect every `iperf` and `ping` within 2 seconds of the command being issued!

```
