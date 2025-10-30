# Federated Learning - MNIST Digit Classification

A distributed machine learning system that trains a neural network across multiple clients without sharing raw data. Built with PyTorch for the Computer Networks course project.

## 🎯 Overview

This project implements **Federated Learning** where:
- Multiple clients train on their local MNIST data
- A central server aggregates model updates using **FedAvg algorithm**
- No raw data is shared - only model weights
- Achieves **95-97% accuracy** after 5 rounds

## 📋 Features

- ✅ Real MNIST dataset integration (60,000 training images)
- ✅ FedAvg aggregation algorithm
- ✅ Automatic model evaluation and accuracy tracking
- ✅ Training visualization with accuracy/loss curves
- ✅ Robust error handling and timeout management
- ✅ Support for multiple clients with unique data partitions

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/PiyushPokharana/Computer_Network-Project.git
cd Computer_Network-Project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure server IP**
   
   Edit `client.py` line 9 to set your server's IP address:
   ```python
   SERVER_IP = "192.168.x.x"  # Replace with actual server IP
   ```
   
   Or use the setup script:
   ```bash
   python setup_ip.py
   ```

### Running the System

#### 1. Start the Server

```bash
python server.py
```

The server will:
- Listen for client connections on port 5000
- Wait for at least 2 clients to connect
- Coordinate 5 rounds of federated training
- Save results to `training_history_[timestamp].json`

#### 2. Start Clients (in separate terminals)

**Windows (PowerShell):**
```powershell
# Terminal 1 - Client 0
$env:CLIENT_ID='0'; python client.py

# Terminal 2 - Client 1
$env:CLIENT_ID='1'; python client.py
```

**Linux/Mac:**
```bash
# Terminal 1 - Client 0
CLIENT_ID=0 python client.py

# Terminal 2 - Client 1
CLIENT_ID=1 python client.py
```

#### 3. Visualize Results

After training completes:
```bash
python visualize_training.py
```

This generates `training_results.png` with accuracy and loss curves.

## 📁 Project Structure

```
├── client.py              # Federated learning client
├── server.py              # Federated learning server
├── model_def.py           # Neural network architecture (MNISTNet)
├── data_utils.py          # Data distribution utilities
├── visualize_training.py  # Training visualization script
├── setup_ip.py            # IP configuration helper
├── test_setup.py          # Environment validation script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Server Configuration (`server.py`)

```python
PORT = 5000              # Server listening port
MIN_CLIENTS = 2          # Minimum clients to start training
NUM_ROUNDS = 5           # Number of training rounds
TIMEOUT = 120            # Client connection timeout (seconds)
```

### Client Configuration (`client.py`)

```python
SERVER_IP = "192.168.x.x"  # Server IP address
PORT = 5000                 # Server port
NUM_CLIENTS = 2             # Total number of clients
```

### Environment Variables

- `CLIENT_ID`: Unique identifier for each client (0, 1, 2, ...)
- `NUM_CLIENTS`: Total number of participating clients (default: 2)

## 📊 Expected Results

| Round | Accuracy | Loss   |
|-------|----------|--------|
| 1     | 85-88%   | 0.45   |
| 2     | 90-92%   | 0.30   |
| 3     | 92-94%   | 0.25   |
| 4     | 94-96%   | 0.20   |
| 5     | 95-97%   | 0.15   |

## 🏗️ Architecture

### MNISTNet Model
```
Input (28×28) → Flatten (784) → FC1 (128) → ReLU → Dropout(0.2)
                                → FC2 (64)  → ReLU → Dropout(0.2)
                                → FC3 (10)  → Output
```

### Communication Protocol
- **Length-prefix protocol**: 4-byte header + serialized data
- **Serialization**: Python pickle
- **Transport**: TCP sockets

### FedAvg Algorithm
1. Server broadcasts global model to all clients
2. Each client trains locally on their data partition
3. Clients send updated weights back to server
4. Server averages weights: `w_global = Σ(n_i/n_total × w_i)`
5. Repeat for multiple rounds

## 🛠️ Troubleshooting

### Connection Issues

**Problem**: `ConnectionRefusedError`

**Solutions**:
1. Verify server is running first
2. Check `SERVER_IP` in `client.py` matches server IP
3. Ensure port 5000 is not blocked by firewall
4. Use `ipconfig` (Windows) or `ifconfig` (Linux/Mac) to find correct IP

### Import Errors

**Problem**: `ImportError: cannot import name 'MNISTNet'`

**Solutions**:
1. Ensure all files are in the same directory
2. Check you're running from the correct directory
3. Verify `model_def.py` contains the `MNISTNet` class

### Timeout Issues

**Problem**: Clients timeout during training

**Solutions**:
1. Increase `TIMEOUT` in `server.py` (default: 120s)
2. Reduce training epochs in `client.py` `local_train()` function
3. Use smaller batch sizes for faster training

## 📚 Dependencies

- `torch>=2.0.0` - PyTorch deep learning framework
- `torchvision>=0.15.0` - MNIST dataset and transforms
- `matplotlib>=3.5.0` - Visualization
- `numpy>=1.21.0` - Numerical operations

## 🧪 Testing

Validate your environment setup:
```bash
python test_setup.py
```

This checks:
- Python version compatibility
- Required packages installation
- Model instantiation
- MNIST data loading

## 📝 Advanced Features

### Non-IID Data Distribution

Use `data_utils.py` for advanced data partitioning:

```python
from data_utils import create_non_iid_split, create_class_based_split

# Non-IID split (clients get different data distributions)
client_loaders = create_non_iid_split(num_clients=3, num_shards=6)

# Class-based split (each client gets specific digit classes)
client_loaders = create_class_based_split(
    num_clients=3, 
    classes_per_client=3
)
```

### Adding More Clients

To run with 3+ clients:

1. Set `MIN_CLIENTS` in `server.py`
2. Set `NUM_CLIENTS=3` in client environment
3. Start additional clients with unique IDs:
   ```powershell
   $env:CLIENT_ID='2'; $env:NUM_CLIENTS='3'; python client.py
   ```

## 🤝 Contributing

This project was developed as part of the Computer Networks course at IIIT Nagpur.

## 📄 License

This project is created for educational purposes.

## 👥 Authors

- **Repository Owner**: [PiyushPokharana](https://github.com/PiyushPokharana)
- **Course**: Computer Networks
- **Institution**: IIIT Nagpur

## 🎓 Acknowledgments

- MNIST dataset from [Yann LeCun's website](http://yann.lecun.com/exdb/mnist/)
- FedAvg algorithm from [McMahan et al. 2017](https://arxiv.org/abs/1602.05629)
- PyTorch framework from [PyTorch Team](https://pytorch.org/)

---

**⭐ If you find this project helpful, please give it a star!**

For questions or issues, please open an issue on GitHub.
