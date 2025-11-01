# Federated Learning with 6G Network Simulation
## Computer Networks Lab Project Report

---

**Course:** Computer Networks Lab  
**Institution:** Indian Institute of Information Technology, Nagpur  
**Semester:** 5th Semester  
**Date:** November 2, 2025  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Introduction](#introduction)
3. [System Architecture](#system-architecture)
4. [Implementation Details](#implementation-details)
5. [Network Simulation](#network-simulation)
6. [Experimental Results](#experimental-results)
7. [Visualization & Monitoring](#visualization--monitoring)
8. [Challenges & Solutions](#challenges--solutions)
9. [Conclusion](#conclusion)
10. [References](#references)
11. [Appendix](#appendix)

---

## Executive Summary

This project implements a **Federated Learning system** with **6G network simulation** for distributed machine learning on MNIST digit classification. The system demonstrates how multiple edge devices can collaboratively train a global model while keeping data localized, simulating real-world 6G network conditions.

### Key Achievements:
- ✅ Implemented FedAvg algorithm with 2 clients
- ✅ Achieved 97.96% accuracy on MNIST dataset
- ✅ Simulated 6G network characteristics (1000 Mbps, 10ms latency)
- ✅ Created 15+ comprehensive visualizations
- ✅ Developed real-time network monitoring tools
- ✅ Total network traffic: 8.38 MB over 5 training rounds

---

## 1. Introduction

### 1.1 Problem Statement

Traditional centralized machine learning requires collecting data from all sources into a central server, raising concerns about:
- **Privacy:** Sensitive data must leave local devices
- **Bandwidth:** Large datasets require significant network resources
- **Latency:** Data transfer and processing time
- **Scalability:** Central server becomes a bottleneck

### 1.2 Proposed Solution

**Federated Learning** enables distributed training where:
- Models are trained locally on edge devices
- Only model updates are shared (not raw data)
- A central server aggregates updates into a global model
- Data privacy is preserved throughout the process

### 1.3 Objectives

1. Implement a working federated learning system
2. Simulate realistic 6G network conditions
3. Achieve competitive accuracy on MNIST dataset
4. Visualize network communication and training progress
5. Analyze performance metrics comprehensively

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FEDERATED LEARNING SYSTEM             │
└─────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────┐
    │           CENTRAL SERVER (Aggregator)         │
    │  - Model aggregation (FedAvg)                 │
    │  - 6G network simulation                      │
    │  - Performance metrics collection             │
    └───────────────┬───────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼─────┐         ┌────▼─────┐
    │ CLIENT 0 │         │ CLIENT 1 │
    │ - Local  │         │ - Local  │
    │   Data   │         │   Data   │
    │ - Local  │         │ - Local  │
    │   Train  │         │   Train  │
    └──────────┘         └──────────┘
```

### 2.2 Component Breakdown

#### **Server Component (`server.py`)**
- **Role:** Central aggregator and coordinator
- **Functions:**
  - Distribute global model to clients
  - Collect trained models from clients
  - Aggregate using FedAvg algorithm
  - Evaluate global model performance
  - Simulate 6G network conditions
  - Track performance metrics

#### **Client Component (`client.py`)**
- **Role:** Edge device simulator
- **Functions:**
  - Load local data partition
  - Train model on local data
  - Send model updates to server
  - Receive updated global model

#### **Model Definition (`model_def.py`)**
- **Architecture:** MNISTNet (3-layer feedforward)
- **Structure:**
  - Input: 784 neurons (28×28 pixels)
  - Hidden 1: 128 neurons (ReLU activation)
  - Hidden 2: 64 neurons (ReLU activation)
  - Output: 10 neurons (softmax for digits 0-9)
- **Total Parameters:** 109,386

#### **Data Management (`data_utils.py`)**
- **Dataset:** MNIST handwritten digits
- **Partitioning:** Non-IID distribution
- **Purpose:** Simulate realistic heterogeneous data across clients

### 2.3 Communication Protocol

```
Round 1-5 (Each Round):
├─ Phase 1: DISTRIBUTE
│  └─ Server → Clients: Global model parameters (437 KB each)
├─ Phase 2: TRAIN
│  └─ Clients: Local training (3 epochs each)
├─ Phase 3: COLLECT
│  └─ Clients → Server: Trained model updates (437 KB each)
├─ Phase 4: AGGREGATE
│  └─ Server: FedAvg aggregation
└─ Phase 5: EVALUATE
   └─ Server: Test on validation set
```

---

## 3. Implementation Details

### 3.1 Neural Network Architecture

**MNISTNet Specifications:**

| Layer | Type | Input Shape | Output Shape | Parameters | Activation |
|-------|------|-------------|--------------|------------|------------|
| fc1 | Linear | 784 | 128 | 100,352 | ReLU |
| fc2 | Linear | 128 | 64 | 8,192 | ReLU |
| fc3 | Linear | 64 | 10 | 640 | Softmax |

**Total Parameters:** 109,386 (100,352 + 128 + 8,192 + 64 + 640 + 10)

**Parameter Distribution:**
- fc1.weight: 91.8% of all parameters
- fc2.weight: 7.5% of all parameters
- fc3.weight: 0.6% of all parameters
- Biases: 0.2% of all parameters

### 3.2 Federated Averaging (FedAvg) Algorithm

**Mathematical Formulation:**

```
Global Model Update:
θ_global^(t+1) = Σ(n_k / N) × θ_k^(t+1)

Where:
- θ_global: Global model parameters
- θ_k: Client k's local model parameters
- n_k: Number of samples at client k
- N: Total number of samples
- t: Current round
```

**Implementation Steps:**
1. Initialize global model θ_0
2. For each round t = 1 to T:
   - Distribute θ_global^(t) to all clients
   - Each client k trains locally: θ_k^(t+1) = LocalUpdate(θ_global^(t), D_k)
   - Collect all θ_k^(t+1)
   - Aggregate: θ_global^(t+1) = FedAvg({θ_k^(t+1)})
3. Return final global model

### 3.3 Training Configuration

**Hyperparameters:**
- **Global Rounds:** 5
- **Local Epochs:** 3 per client per round
- **Batch Size:** 32
- **Learning Rate:** 0.01
- **Optimizer:** SGD with momentum (0.9)
- **Loss Function:** CrossEntropyLoss
- **Number of Clients:** 2

**Data Split:**
- Training: 60,000 samples (30,000 per client)
- Testing: 10,000 samples (centralized evaluation)

### 3.4 Code Structure

```
federated_learning_2/
├── server.py                      # Central server implementation
├── client.py                      # Client implementation
├── model_def.py                   # Neural network definition
├── data_utils.py                  # Data loading & partitioning
├── requirements.txt               # Dependencies
├── visualize_training.py          # Training metrics visualization
├── visualize_metrics.py           # Performance metrics visualization
├── visualize_all.py               # Comprehensive dashboard
├── visualize_network_parameters.py # Network parameter analysis
├── visualize_live_network.py      # Real-time network monitor
├── visualize_live_network_advanced.py # Advanced live monitor
├── monitor.py                     # Real-time training monitor
├── test_implementation.py         # Automated testing
└── data/MNIST/                    # MNIST dataset
```

---

## 4. Network Simulation

### 4.1 6G Network Characteristics

Our implementation simulates realistic 6G network conditions:

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Bandwidth** | 1000 Mbps | High-speed data transfer |
| **Latency** | 10 ms | Base delay |
| **Jitter** | 5 ms | Variation in latency |
| **Packet Loss** | 1% | Random packet drops |
| **Protocol** | TCP | Reliable transmission |

### 4.2 Network Simulation Implementation

**Latency Simulation:**
```python
actual_latency = base_latency + random.uniform(-jitter, jitter)
time.sleep(actual_latency / 1000)  # Convert ms to seconds
```

**Bandwidth Throttling:**
```python
transfer_time = data_size_bytes / (bandwidth_mbps * 1024 * 1024 / 8)
time.sleep(transfer_time)
```

**Packet Loss Simulation:**
```python
if random.random() < packet_loss_rate:
    # Retransmit packet
    retry_transmission()
```

### 4.3 Communication Overhead

**Per Round Network Traffic:**
- Model distribution: 437 KB × 2 clients = 874 KB
- Update collection: 437 KB × 2 clients = 874 KB
- **Total per round:** 1.748 MB

**Total for 5 Rounds:**
- Bytes sent: 4.395 MB
- Bytes received: 4.395 MB
- **Total traffic:** 8.38 MB

**Efficiency Analysis:**
- Model size: 109,386 params × 4 bytes = 437 KB
- Compared to centralized: Would need 60,000 images × 784 bytes = 47 MB
- **Bandwidth savings:** 82% reduction

---

## 5. Experimental Results

### 5.1 Training Performance

**Accuracy Progression:**

| Round | Test Accuracy | Test Loss | Improvement |
|-------|--------------|-----------|-------------|
| 1 | 96.74% | 0.1123 | Baseline |
| 2 | 97.68% | 0.0813 | +0.94% |
| 3 | 97.85% | 0.0779 | +0.17% |
| 4 | 97.85% | 0.0813 | 0.00% |
| 5 | 97.96% | 0.0817 | +0.11% |

**Final Results:**
- **Best Accuracy:** 97.96%
- **Final Loss:** 0.0817
- **Total Improvement:** +1.22%
- **Convergence:** Achieved by round 3

### 5.2 Timing Analysis

**Round Duration Breakdown:**

| Round | Duration (s) | Distribution (s) | Training (s) | Collection (s) | Aggregation (s) |
|-------|-------------|------------------|--------------|----------------|-----------------|
| 1 | 156.02 | ~2 | ~150 | ~2 | 0.001 |
| 2 | 96.54 | ~2 | ~92 | ~2 | 0.001 |
| 3 | 141.28 | ~2 | ~137 | ~2 | 0.001 |
| 4 | 86.05 | ~2 | ~82 | ~2 | 0.001 |
| 5 | 96.95 | ~2 | ~93 | ~2 | 0.001 |

**Summary Statistics:**
- **Total Training Time:** 576.84 seconds (9.61 minutes)
- **Average Round Duration:** 115.37 seconds
- **Network Overhead:** ~3.5% of total time
- **Average Aggregation Time:** 0.9 ms (negligible)

### 5.3 Network Performance

**Data Transfer Metrics:**

| Metric | Value |
|--------|-------|
| Total Data Sent | 4.19 MB |
| Total Data Received | 4.19 MB |
| Total Network Traffic | 8.38 MB |
| Average Traffic per Round | 1.68 MB |
| Average Throughput | 14.88 KB/s |

**Network Efficiency:**
- **Transmission Time:** ~20 seconds total
- **Actual Training Time:** ~554 seconds
- **Network Utilization:** 3.5%
- **No packet loss incidents recorded**

### 5.4 Parameter Analysis

**Weight Statistics (Final Round):**

| Layer | Mean | Std Dev | Min | Max | Parameters |
|-------|------|---------|-----|-----|------------|
| fc1.weight | 0.0015 | 0.0600 | -0.543 | 0.383 | 100,352 |
| fc1.bias | -0.035 | 0.0297 | -0.108 | 0.035 | 128 |
| fc2.weight | -0.015 | 0.1165 | -0.459 | 0.455 | 8,192 |
| fc2.bias | 0.073 | 0.1925 | -0.337 | 0.496 | 64 |
| fc3.weight | 0.001 | 0.2638 | -0.587 | 0.482 | 640 |
| fc3.bias | 0.012 | 0.4558 | -0.376 | 1.225 | 10 |

**Observations:**
- All weight means close to zero ✓
- Standard deviations appropriate for depth ✓
- No exploding/vanishing gradients ✓
- Stable convergence across rounds ✓

---

## 6. Visualization & Monitoring

### 6.1 Static Visualizations (10 PNG files)

#### **Training Metrics:**
1. **training_dashboard.png** - Combined accuracy & loss
2. **training_curves.png** - Detailed training curves
3. **client_participation.png** - Client activity tracking

#### **Performance Metrics:**
4. **performance_metrics.png** - Network & timing analysis
5. **complete_dashboard.png** - All-in-one overview

#### **Network Parameters:**
6. **weight_distributions_round_5.png** - Weight histograms per layer
7. **parameter_evolution.png** - Parameters across rounds
8. **weight_heatmaps_round_5.png** - Weight matrix visualizations
9. **layer_parameter_distribution.png** - Architecture breakdown
10. **comprehensive_parameters_round_5.png** - Complete parameter analysis

### 6.2 Real-Time Monitoring

**Live Network Visualization (`visualize_live_network.py`):**
- Animated network topology (server + clients)
- Real-time packet transmission animation
- Training progress bars (0-100%)
- Live accuracy/loss graphs
- Phase indicators (IDLE, SEND, TRAIN, RECV, AGG)
- Network traffic statistics

**Features:**
- Updates every 0.5 seconds
- Shows 5 distinct training phases
- Color-coded packet types (Model=Blue, Update=Green)
- Progress visualization for each client

### 6.3 Monitoring Tools

1. **monitor.py** - Real-time training progress tracker
2. **test_implementation.py** - Automated testing suite
3. **visualize_live_network_advanced.py** - Advanced monitor with:
   - Dark theme with glow effects
   - Packet trails
   - Latency display
   - Bandwidth graphs
   - GIF export capability

---

## 7. Challenges & Solutions

### 7.1 Technical Challenges

#### **Challenge 1: Port Configuration Mismatch**
- **Problem:** Server listening on port 5000, client connecting to 6000
- **Impact:** Connection refused errors
- **Solution:** 
  - Fixed client.py PORT from 6000 to 5000
  - Made ports configurable via environment variables
  - Added validation and error handling

#### **Challenge 2: Data Structure Inconsistency**
- **Problem:** Visualization tools expected dictionary format, but JSON had array format
- **Impact:** TypeError when reading training_history.json
- **Solution:** 
  - Updated visualization scripts to handle array format
  - Added fallback mechanisms for missing data

#### **Challenge 3: Network Simulation Accuracy**
- **Problem:** Ensuring realistic 6G network behavior
- **Impact:** Artificial timing, unrealistic results
- **Solution:**
  - Implemented proper latency simulation with jitter
  - Added bandwidth throttling
  - Included packet loss simulation
  - Validated against real-world 6G specs

#### **Challenge 4: Non-IID Data Distribution**
- **Problem:** Creating realistic heterogeneous data splits
- **Impact:** Clients might get unbalanced data
- **Solution:**
  - Implemented label-based partitioning
  - Ensured each client gets diverse samples
  - Validated distribution fairness

### 7.2 Performance Optimizations

1. **Model Compression:** Could implement gradient quantization (future work)
2. **Caching:** Implemented metrics caching to reduce I/O
3. **Parallel Processing:** Clients train simultaneously
4. **Efficient Aggregation:** NumPy vectorization for FedAvg

### 7.3 Lessons Learned

1. **Configuration Management:** Environment variables crucial for flexibility
2. **Comprehensive Testing:** Automated tests catch issues early
3. **Documentation:** Detailed guides improve usability
4. **Visualization:** Real-time monitoring invaluable for debugging
5. **Modularity:** Separate concerns (network, training, visualization)

---

## 8. Conclusion

### 8.1 Summary of Achievements

This project successfully demonstrates a complete federated learning system with:

✅ **Functional Implementation:**
- Working FL system with 2 clients
- FedAvg aggregation algorithm
- 97.96% final accuracy on MNIST

✅ **Network Simulation:**
- Realistic 6G characteristics (1000 Mbps, 10ms latency)
- Total traffic: 8.38 MB
- 82% bandwidth savings vs centralized approach

✅ **Comprehensive Visualization:**
- 10 static visualizations covering all aspects
- Real-time network animation
- Parameter evolution tracking
- Performance metrics dashboard

✅ **Documentation:**
- 8 detailed markdown guides
- Code comments and docstrings
- Usage examples and tutorials

### 8.2 Key Findings

1. **Federated Learning is Viable:**
   - Achieved competitive accuracy (97.96%)
   - Preserved data privacy
   - Reduced network traffic by 82%

2. **6G Enables FL:**
   - High bandwidth (1000 Mbps) supports rapid model transfer
   - Low latency (10ms) minimizes communication overhead
   - Reliable transmission ensures convergence

3. **Scalability Considerations:**
   - Linear network traffic growth with clients
   - Aggregation time remains constant
   - Training time depends on slowest client

### 8.3 Future Work

#### **Short-term Enhancements:**
1. Increase number of clients (3-10)
2. Implement client selection strategies
3. Add differential privacy mechanisms
4. Test on larger datasets (CIFAR-10, ImageNet)

#### **Advanced Features:**
1. **FedProx Algorithm:** Handle system heterogeneity
2. **Secure Aggregation:** Cryptographic privacy guarantees
3. **Asynchronous Updates:** Don't wait for slow clients
4. **Model Compression:** Reduce communication costs
5. **Byzantine-Robust Aggregation:** Handle malicious clients

#### **Network Improvements:**
1. Simulate different network conditions (4G, 5G, 6G)
2. Model network congestion
3. Implement adaptive bandwidth allocation
4. Test cross-silo federated learning

### 8.4 Real-World Applications

This implementation can be adapted for:

1. **Healthcare:** Hospital-distributed disease prediction
2. **Finance:** Cross-bank fraud detection
3. **IoT:** Smart home device learning
4. **Mobile:** Keyboard prediction training
5. **Automotive:** Autonomous vehicle learning

---

## 9. References

### Academic Papers:
1. McMahan, B., et al. (2017). "Communication-Efficient Learning of Deep Networks from Decentralized Data." AISTATS.
2. Li, T., et al. (2020). "Federated Optimization in Heterogeneous Networks." MLSys.
3. Kairouz, P., et al. (2021). "Advances and Open Problems in Federated Learning." Foundations and Trends in Machine Learning.

### Technical Documentation:
4. PyTorch Documentation - https://pytorch.org/docs/
5. 6G Network Specifications - ITU-R IMT-2030
6. MNIST Dataset - http://yann.lecun.com/exdb/mnist/

### Repositories:
7. This Project - https://github.com/The-Harsh-Vardhan/federated_learning
8. FL Tutorials - https://flower.dev/docs/

---

## 10. Appendix

### A. System Requirements

**Hardware:**
- CPU: Multi-core processor (4+ cores recommended)
- RAM: 8GB minimum, 16GB recommended
- Storage: 2GB free space
- Network: 100 Mbps+ for optimal performance

**Software:**
- Python 3.9+
- PyTorch 2.0+
- Matplotlib 3.5+
- NumPy 1.21+
- Virtual environment (venv)

### B. Installation Instructions

```powershell
# Clone repository
git clone https://github.com/The-Harsh-Vardhan/federated_learning.git
cd federated_learning_2

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_implementation.py
```

### C. Quick Start Commands

```powershell
# Terminal 1: Start server
$env:SERVER_HOST="127.0.0.1"; $env:SERVER_PORT="5000"; python server.py

# Terminal 2: Start client 0
$env:SERVER_IP="127.0.0.1"; $env:CLIENT_ID="0"; python client.py

# Terminal 3: Start client 1
$env:SERVER_IP="127.0.0.1"; $env:CLIENT_ID="1"; python client.py

# Terminal 4: Visualize results
python visualize_all.py
python visualize_network_parameters.py
python visualize_live_network.py
```

### D. Configuration Options

**Environment Variables:**
- `SERVER_HOST`: Server IP address (default: "192.168.109.142")
- `SERVER_PORT`: Server port (default: 5000)
- `CLIENT_ID`: Client identifier (0, 1, 2, ...)
- `NUM_CLIENTS`: Total number of clients (default: 2)

**Training Parameters (in code):**
- `NUM_ROUNDS`: Number of federated rounds
- `LOCAL_EPOCHS`: Epochs per client per round
- `BATCH_SIZE`: Mini-batch size
- `LEARNING_RATE`: SGD learning rate

### E. File Descriptions

**Core Files:**
- `server.py` (450+ lines): Server implementation with metrics
- `client.py` (200+ lines): Client implementation
- `model_def.py` (30 lines): Neural network architecture
- `data_utils.py` (100+ lines): Data loading utilities

**Visualization Files:**
- `visualize_training.py` (230 lines): Training metrics
- `visualize_metrics.py` (160 lines): Performance metrics
- `visualize_all.py` (230 lines): Comprehensive dashboard
- `visualize_network_parameters.py` (470 lines): Parameter analysis
- `visualize_live_network.py` (350 lines): Real-time monitor
- `visualize_live_network_advanced.py` (650 lines): Advanced monitor

**Utility Files:**
- `monitor.py` (90 lines): Real-time training tracker
- `test_implementation.py` (130 lines): Automated tests

**Documentation:**
- 8 markdown guides covering all aspects

### F. Troubleshooting

**Common Issues:**

1. **"Connection refused"**
   - Check if server is running
   - Verify ports match (default: 5000)
   - Check firewall settings

2. **"No module named 'torch'"**
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

3. **"CUDA not available"**
   - Normal - code runs on CPU
   - For GPU: Install CUDA-enabled PyTorch

4. **Visualization window doesn't open**
   - Install matplotlib backend
   - Check display settings
   - Try different terminal

### G. Performance Benchmarks

**Training Time (9.61 minutes total):**
- Model initialization: <1 second
- Round 1: 156 seconds
- Rounds 2-5: 86-141 seconds each
- Evaluation per round: ~1.8 seconds

**Memory Usage:**
- Server: ~300 MB
- Client: ~200 MB each
- Peak: ~700 MB total

**Network Traffic:**
- Per round: 1.68 MB
- Total: 8.38 MB
- Efficiency: 82% savings vs centralized

### H. Project Statistics

**Code Metrics:**
- Total Lines of Code: ~3,000+
- Python Files: 15
- Visualization Scripts: 6
- Documentation Files: 8
- Total Repository Size: ~50 MB (with dataset)

**Development Timeline:**
- Planning: 2 days
- Core Implementation: 5 days
- Visualization Development: 3 days
- Testing & Debugging: 2 days
- Documentation: 2 days
- **Total: ~2 weeks**

---

## Acknowledgments

This project was developed as part of the Computer Networks Lab curriculum at Indian Institute of Information Technology, Nagpur. Special thanks to:

- Course instructors for guidance
- PyTorch community for excellent documentation
- Open-source federated learning community
- GitHub Copilot for development assistance

---

## Contact Information

**Repository:** https://github.com/The-Harsh-Vardhan/federated_learning  
**Institution:** IIIT Nagpur  
**Course:** Computer Networks Lab  
**Semester:** 5th Semester, 2025  

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Report Generated:** November 2, 2025  
**Project Version:** 2.0  
**Status:** Complete and Operational ✅

---

*End of Report*
