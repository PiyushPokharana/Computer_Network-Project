# Federated Learning in Simulated 6G Networks

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python implementation of Federated Learning (FL) in a simulated 6G network environment. This project demonstrates privacy-preserving distributed machine learning where multiple clients collaboratively train a global model without sharing their local data.

## 🎯 Project Overview

This project simulates a federated learning system where:
- 🖥️ A central server coordinates the training process
- 📱 Multiple clients train locally on their own data
- 🔄 Model updates (not raw data) are shared across the network
- 🔒 Privacy is preserved through local data storage
- 📡 6G network characteristics can be simulated

## 📚 Quick Links

- [Quickstart Guide](QUICKSTART.md) - Get started in 5 minutes
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history and updates
- [License](LICENSE) - MIT License

## Part 1: What is Federated Learning (FL)?

### Traditional ML
In standard machine learning:
- You collect all data in one place (e.g., cloud)
- Train a model centrally

But this is often impractical or unsafe when data is private or distributed (e.g., hospitals, phones, IoT sensors).

### Federated Learning
Federated Learning solves that by keeping data local.

It works like this:
1. A central server (aggregator) sends a global model to many devices ("clients")
2. Each device:
   - Trains the model on its own local data
   - Sends only model updates (weights or gradients) back — **not the data itself**
3. The server aggregates all updates (usually by averaging → **FedAvg**)
4. The updated model is redistributed to all clients
5. Repeat for several rounds

So, the model "learns from everyone" without ever seeing raw data.

#### 💡 Analogy
> "Each student (client) studies their local notes, updates a shared class summary, and sends it to the teacher (server), who merges all inputs into a better global summary — without ever collecting their notes."

#### Key Benefits
- **Privacy:** Data never leaves the device
- **Efficiency:** Less raw data transmission
- **Scalability:** Many devices can train together

---

## Part 2: What is a 6G Network?

6G is the next generation after 5G, expected around **2030**. It will be the backbone for AI-driven, hyper-connected, low-latency systems.

| Feature | Description |
|---------|-------------|
| **Latency** | < 1 millisecond (very low) |
| **Bandwidth** | Up to 1 Tbps |
| **Reliability** | Ultra-high — critical for real-time AI |
| **Edge Intelligence** | AI processing happens close to users (not just in the cloud) |
| **Massive Connectivity** | Trillions of IoT/edge devices |
| **Energy Efficiency** | Sustainable and adaptive communication |
| **Integration** | Combines communication, sensing, and computing in one ecosystem |

---

## Part 3: Why Combine Federated Learning with 6G?

Because 6G networks are designed for intelligent, distributed computing, Federated Learning (FL) becomes a core enabler of 6G intelligence.

### Here's why:

| 6G Capability | Federated Learning Benefit |
|---------------|----------------------------|
| **Edge computing** | FL allows model training directly on edge nodes |
| **High bandwidth** | Faster model updates, larger models |
| **Low latency** | Enables near real-time global model aggregation |
| **Privacy-preserving AI** | FL ensures user data stays local |
| **Distributed architecture** | FL naturally fits into multi-node edge systems |
| **AI-native networks** | 6G itself uses FL to optimize its own performance |

**So — Federated Learning isn't just an application in 6G — it's part of how 6G itself will operate intelligently.**

---

## Part 4: What "Simulated 6G Networks" Means

When we say "simulated 6G networks," we mean we're not running on real 6G infrastructure (since it doesn't exist yet), but we simulate the important network characteristics in software.

### We model:
- **Latency:** Time delay in communication
- **Bandwidth:** Maximum data transmission rate
- **Packet loss:** Random loss of messages or updates
- **Client heterogeneity:** Different hardware speeds and data distributions
- **Energy limits:** Battery constraints (optional)

So, your simulation replicates a virtual 6G edge network, where:
- Devices act as edge nodes
- The server acts as the 6G core or aggregator
- Communication conditions are mathematically simulated (using parameters)

In a simulated 6G environment, you don't need real 6G hardware — you mathematically or virtually model the networking characteristics that 6G would offer (or limit):

| Factor | Meaning | How it affects Federated Learning (FL) | How we simulate it |
|--------|---------|----------------------------------------|-------------------|
| **Latency** | Time delay between sending and receiving data | High latency slows down synchronization between clients and server | Add artificial time delay before/after communication (in code) or via `tc netem delay` |
| **Bandwidth** | Maximum data transfer rate (e.g., Mbps, Gbps) | Low bandwidth increases round time for model uploads/downloads | Limit data rate in code or use `tc tbf rate` |
| **Jitter** | Variability in packet delay | Causes unpredictable communication time | Add random variation to delay |
| **Packet Loss** | % of packets lost during transfer | Leads to retransmission or update failure | Randomly drop some updates or use `tc netem loss` |
| **Throughput** | Actual achieved transfer rate | Determines real performance under congestion | Measured result of bandwidth + latency + jitter |
| **Device Heterogeneity** | Different compute speeds, energy levels | Slower clients (stragglers) slow global rounds | Add variable local training time |
| **Mobility / Handover** (advanced) | Clients moving between base stations | Causes latency spikes or disconnects | Randomly reset network profiles mid-simulation |

### In essence:
> We can simulate every aspect of a communication network that affects FL — from edge device constraints (low bandwidth, high latency) to idealized 6G-like ultra-low-latency, high-throughput links — and study how the federated learning model's convergence and efficiency respond.

**So:**
- We don't need a physical 6G setup
- We can run all tests locally or across LAN devices
- And we can control all these parameters programmatically, dynamically, or through Linux tools

---

## Running FL on Multiple Real Devices

Running your federated learning (FL) simulation on multiple real devices (like laptops connected to your campus LAN) is actually quite easy once you understand the setup. You don't need special hardware or 6G access points — just a local Wi-Fi or Ethernet network that connects all the devices.

### ⚙️ 1. What Happens in Multi-Device FL Setup

- One machine acts as the **FL server / aggregator**
- Other machines act as **FL clients / edge devices**
- They all communicate via normal TCP sockets (e.g., `socket`, `flask`, `gRPC`, or frameworks like Flower)
- The LAN simply provides IP connectivity — **no Internet needed**

#### 💡 Think of it like this:
- Each laptop = 1 simulated 6G edge node
- The LAN = the "network channel" between clients and server

Then you can use network emulation (`tc`, `netem`, or your Python simulator) to imitate the characteristics of a 6G link — latency, bandwidth, jitter, loss — even though you're just using normal Wi-Fi.

---

### 🛠️ 2. Requirements (Local Setup)

| Component | Description |
|-----------|-------------|
| **LAN connectivity** | All laptops on same Wi-Fi or Ethernet subnet |
| **Python (3.9+)** | Same environment on all devices |
| **Common model/data** | Each client has its own small dataset |
| **Server IP** | One laptop's local IP (use `ipconfig` / `ifconfig`) |
| **Open ports** | e.g. port 8080 or 5000 for communication |
| **Firewall off or port allowed** | So others can connect |

---

### 🌐 3. Architecture Example

```
+----------------------------+
|   Server (Aggregator)      |
|   IP: 192.168.1.10         |
|   Runs: server.py          |
|   Role: coordinate global  |
|   rounds and model updates |
+-------------^--------------+
              |
      (LAN, e.g. Wi-Fi)
              |
+-------------+--------------+
| Client 1 (Edge Device A)   |
| IP: 192.168.1.11           |
| Runs: client.py --server 192.168.1.10 |
+----------------------------+
| Client 2 (Edge Device B)   |
| IP: 192.168.1.12           |
| Runs: client.py --server 192.168.1.10 |
+----------------------------+
```

---

### 🔄 4. How the Process Works

1. **Server starts first** – waits for clients to connect
2. **Clients connect** to the server's IP:port
3. **Server sends** current global model
4. **Each client trains** locally and returns model updates
5. **Server aggregates** updates (e.g., FedAvg)
6. **Repeat** for multiple communication rounds
7. **Metrics** (accuracy, latency, bandwidth usage) logged each round

---

### ✅ 5. Why LAN Deployment is Ideal for You

- **Fast** (latency usually <5 ms)
- **Reliable** (low packet loss)
- **Easy to debug**
- Works with network emulation tools for more realism

---

## Project Structure

```
federated_learning/
├── client.py          # FL client implementation
├── server.py          # FL server/aggregator
├── model_def.py       # Neural network model definition
├── Readme.md          # This file
└── venv/              # Python virtual environment
```

---

## Setup Instructions

### 1. Create and activate virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\python.exe
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install torch
```

### 3. Running the server

```bash
python server.py
```

### 4. Running clients (on same or different machines)

Update `SERVER_IP` in `client.py` or set environment variable:

```bash
# Using environment variable
export SERVER_IP=192.168.1.10  # Or your server's IP
export SERVER_PORT=5000
python client.py
```

Or run directly with venv:
```bash
.\venv\Scripts\python.exe client.py
```

---

## Features

### Client Features:
- ✅ Local model training with dummy data
- ✅ Secure model weight transmission (length-prefixed protocol)
- ✅ Error handling for network issues
- ✅ Configurable via environment variables
- ✅ Timeout protection (30 seconds)

### Server Features:
- 🔄 Global model aggregation (FedAvg)
- 📊 Multi-client support
- 🔄 Multiple training rounds

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_IP` | `192.168.2.32` | Server IP address |
| `SERVER_PORT` | `5000` | Server port number |

---

## Contributing

This project is part of a Computer Networks course project at IIIT Nagpur demonstrating Federated Learning concepts in simulated 6G network environments.

---

## License

Educational project - IIIT Nagpur

---

## References

- Federated Learning: Collaborative Machine Learning without Centralized Training Data
- 6G Networks: The Next Horizon for Wireless Communications
- FedAvg Algorithm: Communication-Efficient Learning of Deep Networks
