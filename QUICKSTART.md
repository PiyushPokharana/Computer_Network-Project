# Quickstart Guide

This guide will help you get started with the Federated Learning 6G simulation quickly.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Multiple devices on the same network (optional, but recommended)

## Quick Setup (Single Machine)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/federated_learning.git
cd federated_learning
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
# If you get execution policy error, use:
.\venv\Scripts\python.exe
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment (optional)
```bash
cp .env.example .env
# Edit .env file with your settings
```

## Running the Simulation

### Terminal 1: Start the Server
```bash
python server.py
```

You should see:
```
🚀 Server listening on 0.0.0.0:5000
📊 Waiting for 2 clients
🔄 Training rounds: 3
```

### Terminal 2: Start Client 1
```bash
python client.py
```

### Terminal 3: Start Client 2
```bash
python client.py
```

## Multi-Device Setup

### On Server Machine:

1. Find your IP address:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` or `ip addr`

2. Start server:
   ```bash
   python server.py
   ```

### On Client Machines:

1. Set server IP:
   ```bash
   # Windows (PowerShell)
   $env:SERVER_IP="192.168.1.10"
   
   # Linux/Mac
   export SERVER_IP="192.168.1.10"
   ```

2. Start client:
   ```bash
   python client.py
   ```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_IP` | `192.168.2.32` | Server IP address |
| `SERVER_PORT` | `5000` | Server port |
| `NUM_CLIENTS` | `2` | Number of clients per round |
| `NUM_ROUNDS` | `3` | Number of training rounds |

### Example: Custom Configuration

```bash
# Set environment variables
export SERVER_IP="192.168.1.100"
export SERVER_PORT="8080"
export NUM_CLIENTS="3"
export NUM_ROUNDS="5"

# Start server with custom settings
python server.py

# Start clients (in separate terminals)
python client.py
```

## Expected Output

### Server Output:
```
🚀 Server listening on 0.0.0.0:5000
📊 Waiting for 2 clients
🔄 Training rounds: 3

==================================================
📍 Round 1/3
==================================================
✅ Client 1 connected from ('192.168.1.11', 54321)
   📤 Sending global model to Client 1...
   ✓ Model sent to Client 1
   📥 Waiting for updates from Client 1...
   ✓ Received updates from Client 1
...
```

### Client Output:
```
Connected to server at 192.168.2.32:5000
Receiving global model...
Global model loaded successfully
Starting local training...
Local training complete
Sending updated model to server...
Updated model sent successfully
Connection closed
```

## Troubleshooting

### Connection Refused
- Make sure server is running before starting clients
- Check firewall settings
- Verify IP address and port

### Module Not Found
```bash
pip install -r requirements.txt
```

### Timeout Errors
- Increase timeout in client.py (line 72): `client.settimeout(60)`
- Check network connectivity
- Verify server is responding

## Next Steps

- Read the full [README.md](Readme.md) for detailed concepts
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Explore the code to understand FL implementation
- Modify `model_def.py` to experiment with different models
- Adjust training parameters in `client.py`

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review the code comments

Happy Learning! 🚀
