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

## 🎨 Key Features

### ✨ Core Implementation
- **Federated Averaging (FedAvg)** - Standard FL aggregation algorithm
- **Non-IID Data Distribution** - Realistic client data heterogeneity
- **6G Network Simulation** - Configurable latency, bandwidth, jitter, packet loss
- **TCP Socket Communication** - Secure model weight transmission
- **MNIST Dataset** - Handwritten digit classification (28x28 images)

### 📊 Advanced Visualizations (15+ Charts)
- **Training Curves** - Accuracy and loss over rounds
- **Parameter Evolution** - Weight/bias changes across layers
- **Network Analysis** - Throughput, latency, packet loss metrics
- **Live Network Animation** - Real-time packet transmission visualization
- **Performance Dashboards** - Comprehensive metrics overview

### 🔧 Monitoring & Analysis Tools
- Real-time training monitor
- Automated testing suite
- Performance metrics collection
- Network parameter analysis
- Parameter snapshots per round

### 📈 Project Results
- **Accuracy**: 97.96% on MNIST test set
- **Total Traffic**: 8.38 MB across all rounds
- **Training Time**: 9.61 minutes (5 rounds)
- **Model Size**: 109,386 parameters

---

## 📁 Project Structure

```
federated_learning_2/
├── 🐍 Core Python Files
│   ├── server.py                    # FL server with metrics collection
│   ├── client.py                    # FL client with 6G simulation
│   ├── model_def.py                 # Neural network (MNISTNet)
│   └── data_utils.py                # Data loading & partitioning
│
├── 📊 Visualization Scripts
│   ├── visualize_training.py        # Training curves & metrics
│   ├── visualize_metrics.py         # Performance analysis
│   ├── visualize_all.py             # Comprehensive dashboard
│   ├── visualize_network_parameters.py  # 15+ network visualizations
│   ├── visualize_live_network.py    # Basic live animation
│   └── visualize_live_network_advanced.py  # Enhanced live animation
│
├── 🔧 Tools
│   ├── monitor.py                   # Real-time training monitor
│   └── test_implementation.py       # Automated testing
│
├── 📚 Documentation
│   ├── PROJECT_REPORT.md            # Comprehensive 30+ page report
│   ├── PRESENTATION_GUIDE.md        # 15-page presentation guide
│   ├── HOW_TO_RUN.md               # Step-by-step execution guide
│   ├── IMPLEMENTATION_GUIDE.md      # Technical implementation details
│   ├── ALL_VISUALIZATIONS.md        # Complete visualization reference
│   ├── LIVE_VISUALIZATION_GUIDE.md  # Animation usage guide
│   ├── NETWORK_PARAMETERS_EXPLAINED.md  # Parameter analysis
│   ├── QUICKSTART.md               # Get started in 5 minutes
│   ├── CHANGELOG.md                # Version history
│   ├── CONTRIBUTING.md             # Contribution guidelines
│   └── GITHUB_SETUP.md             # GitHub configuration guide
│
├── 🗂️ Configuration
│   ├── requirements.txt             # Python dependencies
│   ├── setup.py                    # Package installation
│   └── .gitignore                  # Git exclusions
│
├── 📦 Data & Models
│   ├── data/MNIST/                 # MNIST dataset (auto-downloaded)
│   └── venv/                       # Python virtual environment
│
└── 🗃️ Extras/
    ├── generated_outputs/          # Training outputs (JSON, PTH)
    ├── visualizations/             # Generated PNG charts
    ├── parameter_snapshots/        # Per-round parameter saves
    └── extra_docs/                 # Additional documentation
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

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- PyTorch 2.0+
- Matplotlib, Seaborn, Pandas
- 2+ GB RAM (for MNIST dataset)
- Network connectivity (for multi-device setup)

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/The-Harsh-Vardhan/federated_learning.git
cd federated_learning_2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System

**Step 1: Start the server**
```bash
python server.py
```

**Step 2: Start clients (in separate terminals)**
```bash
# Client 1
python client.py

# Client 2 (on same or different machine)
export SERVER_IP=192.168.1.10  # Set to server's IP
python client.py
```

**Step 3: Monitor training (optional)**
```bash
# In another terminal
python monitor.py
```

**Step 4: Generate visualizations (after training)**
```bash
# All visualizations at once
python visualize_all.py

# Or specific visualizations
python visualize_training.py
python visualize_network_parameters.py

# Live network animation (during training)
python visualize_live_network_advanced.py
```

For detailed instructions, see [HOW_TO_RUN.md](HOW_TO_RUN.md).

---

## 📊 Visualization Gallery

This project includes 15+ different visualizations:

| Visualization | Description | Output |
|---------------|-------------|--------|
| **Training Curves** | Accuracy and loss over rounds | `training_curves.png` |
| **Complete Dashboard** | 6-panel overview | `complete_dashboard.png` |
| **Parameter Evolution** | Weight changes per layer | `parameter_evolution.png` |
| **Weight Heatmaps** | Visual representation of weights | `weight_heatmaps_round_*.png` |
| **Network Throughput** | Data transfer rates | `network_throughput.png` |
| **Latency Analysis** | Communication delays | `latency_distribution.png` |
| **Packet Loss** | Network reliability | `packet_loss.png` |
| **Live Animation** | Real-time packet transmission | `network_animation.gif` |

See [ALL_VISUALIZATIONS.md](ALL_VISUALIZATIONS.md) for complete gallery.

---

## 🔬 Technical Details

### Model Architecture (MNISTNet)
```
Input Layer:    784 neurons (28x28 flattened)
Hidden Layer 1: 128 neurons + ReLU
Hidden Layer 2: 64 neurons + ReLU
Output Layer:   10 neurons (digits 0-9)
Total Params:   109,386 parameters
```

### 6G Network Simulation Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| Bandwidth | 1000 Mbps | Maximum data rate |
| Base Latency | 10 ms | Minimum delay |
| Jitter | 5 ms | Delay variation |
| Packet Loss | 1% | Random packet drops |
| Model Size | ~220 KB | Per transmission |

### Federated Learning Configuration
| Setting | Value | Notes |
|---------|-------|-------|
| Algorithm | FedAvg | Standard averaging |
| Clients | 2 | Configurable |
| Local Epochs | 1 | Per client per round |
| Global Rounds | 5 | Server iterations |
| Batch Size | 64 | For local training |
| Learning Rate | 0.001 | Adam optimizer |
| Data Split | Non-IID | 60/40 split |

---

## 🎓 Educational Value

This project demonstrates:
- **Distributed Machine Learning** - Training without centralized data
- **Network Simulation** - Modeling 6G characteristics
- **Socket Programming** - TCP client-server architecture
- **Data Visualization** - Comprehensive analysis tools
- **Software Engineering** - Modular design, testing, documentation

Ideal for:
- Computer Networks course projects
- Machine Learning assignments
- Distributed Systems labs
- Research in Federated Learning
- 6G network simulation studies

---

## � Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_REPORT.md](PROJECT_REPORT.md) | Complete 30+ page technical report |
| [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md) | 15-page presentation-focused summary |
| [HOW_TO_RUN.md](HOW_TO_RUN.md) | Step-by-step execution instructions |
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | Technical implementation details |
| [ALL_VISUALIZATIONS.md](ALL_VISUALIZATIONS.md) | Complete visualization gallery |
| [NETWORK_PARAMETERS_EXPLAINED.md](NETWORK_PARAMETERS_EXPLAINED.md) | Network analysis guide |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |

---

## � Troubleshooting

### Common Issues

**"Address already in use" error**
```bash
# Windows: Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Module not found errors**
```bash
# Ensure you're in virtual environment
pip install -r requirements.txt
```

**Connection refused**
```bash
# Check server is running and firewall allows port 5000
# Update SERVER_IP environment variable
```

**MNIST download fails**
```bash
# Manually download to data/MNIST/raw/
# Or use VPN if blocked
```

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for more troubleshooting.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_IP` | `192.168.2.32` | Server IP address |
| `SERVER_PORT` | `5000` | Server port number |

---

## 🤝 Contributing

Contributions are welcome! This project is part of ongoing research and educational efforts in Federated Learning and 6G networks.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Areas for Contribution
- Additional network simulation models
- New visualization techniques
- Performance optimizations
- Enhanced client selection strategies
- Advanced aggregation algorithms
- Better documentation
- Bug fixes and testing

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

This is an educational project developed at IIIT Nagpur for demonstrating Federated Learning concepts in simulated 6G network environments.

---

## 👨‍💻 Authors

**Harsh Vardhan**
- GitHub: [@The-Harsh-Vardhan](https://github.com/The-Harsh-Vardhan)
- Institution: Indian Institute of Information Technology, Nagpur
- Course: Computer Networks Lab (5th Semester)

---

## 🙏 Acknowledgments

- IIIT Nagpur for providing the platform and resources
- PyTorch team for the deep learning framework
- Federated Learning research community
- Open source contributors

---

## 📚 References

### Federated Learning
- McMahan, B., et al. (2017). "Communication-Efficient Learning of Deep Networks from Decentralized Data"
- Kairouz, P., et al. (2021). "Advances and Open Problems in Federated Learning"
- Li, T., et al. (2020). "Federated Learning: Challenges, Methods, and Future Directions"

### 6G Networks
- Letaief, K. B., et al. (2021). "The Roadmap to 6G: AI Empowered Wireless Networks"
- Saad, W., et al. (2020). "A Vision of 6G Wireless Systems: Applications, Trends, Technologies, and Open Research Problems"
- Nguyen, D. C., et al. (2022). "6G Internet of Things: A Comprehensive Survey"

### Distributed Machine Learning
- Dean, J., et al. (2012). "Large Scale Distributed Deep Networks"
- Li, M., et al. (2014). "Scaling Distributed Machine Learning with the Parameter Server"

---

## 📧 Contact & Support

- **Issues**: Please use the [GitHub Issues](https://github.com/The-Harsh-Vardhan/federated_learning/issues) page
- **Discussions**: For questions and discussions, use [GitHub Discussions](https://github.com/The-Harsh-Vardhan/federated_learning/discussions)
- **Email**: For private inquiries, contact through GitHub profile

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐ on GitHub!

---

## 📊 Project Status

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen)

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Active Development

---

<div align="center">

### Made with ❤️ for learning and research

**[⬆ Back to Top](#federated-learning-in-simulated-6g-networks)**

</div>
