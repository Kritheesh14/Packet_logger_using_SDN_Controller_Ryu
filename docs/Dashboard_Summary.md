
# 📊 Dashboard Overview & Manual Testing

This document explains the components of the SDN Monitoring Dashboard and provides methods to manually "stress test" or tamper with the visualizations for demonstration purposes.

## 1. Dashboard Components
The dashboard is a client-side JavaScript application that consumes the Ryu REST API.

* **KPI Cards:** Displays the cumulative count of packets since the controller started.
* **Protocol Distribution (Chart.js):** A dynamic bar chart showing the ratio of network traffic.
* **Live Logs:** A scrollable table showing the last 100 packets with timestamps and MAC addresses.


<img width="1421" height="1056" alt="image" src="https://github.com/user-attachments/assets/e4e938fe-fad2-4927-a465-08eb4b22eb33" />


---

## 2. Manual Testing: Surging Graph Values
If you want to demonstrate the dashboard's responsiveness without generating real network load, you can use these "Terminal Injection" methods.

### A. Generating a TCP/UDP Surge (The "Real" Way)
To see the TCP or UDP bars rise naturally, run these commands in your **Mininet terminal**:

**For a TCP Surge:**
```bash
# Simulates a high-speed file transfer
mininet> h1 iperf -c h2 -t 10
```
<img width="1350" height="1096" alt="image" src="https://github.com/user-attachments/assets/7b111da5-653e-49d7-9f29-9e898a3c3466" />

**For a UDP Surge:**
```bash
# Simulates a 10Mbps video stream
mininet> h1 iperf -u -c h2 -b 10M -t 10
```

<img width="1304" height="1097" alt="image" src="https://github.com/user-attachments/assets/3999f8ff-bf52-4119-93d1-a0332a13fe64" />


### B. Manually Tampering with Values (The "Script" Way)
If you want to "force" the graphs to specific values for a presentation (e.g., showing a massive UDP spike), you can use a Python "Tamper Script" within your `ryu-vm` environment.

1. Create a file named `tamper.py`:
```python
import requests

# The Ryu API endpoint
URL = "[http://127.0.0.1:8080/stats](http://127.0.0.1:8080/stats)"

# Note: Since the actual controller updates these values every packet, 
# manual tampering requires pausing the controller or modifying the 
# internal 'self.counters' dictionary in p_log.py.
```

**The preferred way to tamper for a demo:**
Modify the `self.counters` initialization in `controller/p_log.py` to start with high values:
```python
# Change this line in p_log.py __init__:
self.counters = {"total": 5000, "TCP": 2500, "UDP": 2000, "ICMP": 300, "ARP": 200, "OTHER": 0}
```
*Restart the controller, and your dashboard will immediately load with these "surged" values.*

---

## 3. Configuration Variables
You can alter the dashboard behavior by editing the `<script>` tag in `dashboard/index.html`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `setInterval(..., 2000)` | `2000` | Change to `500` for high-frequency (0.5s) updates. |
| `data.logs.map(...)` | `100` | Alter the `maxlen` in `p_log.py` to show more/fewer log rows. |
| `backgroundColor` | `#bb86fc` | Change the HEX codes to alter the theme colors. |

---

## 4. Resetting Stats
To clear all graphs and logs back to zero, simply restart the Ryu controller:
1.  Go to the Ryu terminal.
2.  Press `Ctrl + C`.
3.  Run `ryu-manager controller/p_log.py` again.
```

