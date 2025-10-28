# Federated Learning System

A simple federated learning implementation using PyTorch with a client-server architecture.

## 🔧 Fixed Issues

### Critical Bugs Fixed:
1. **Client data reception protocol mismatch** - Client now properly handles length-prefixed data from server
2. **Client data sending protocol mismatch** - Client now sends data with length prefix matching server expectations
3. **Missing minimum client threshold** - Server now requires at least 2 clients before proceeding with aggregation
4. **Poor error handling** - Added comprehensive error messages and graceful degradation

### Improvements Added:
- ✅ Minimum client threshold (MIN_CLIENTS = 2) - server waits for at least 2 clients
- ✅ Better logging with detailed progress messages
- ✅ Proper timeout handling (60s per client, 120s for client connection)
- ✅ Connection error recovery
- ✅ Validation that prevents aggregation when minimum clients not met
- ✅ Clear status messages for debugging

## 📁 Files

- `server.py` - Federated learning server that aggregates client models
- `client.py` - Client that trains on local data and sends updates
- `model_def.py` - Neural network model definition (SimpleNet)
- `global_model.pth` - Saved global model after training (generated)

## 🚀 Usage

### 1. Start the Server

```powershell
cd P:\CN_project\working
python server.py
```

**Environment Variables (optional):**
```powershell
$env:SERVER_HOST="0.0.0.0"
$env:SERVER_PORT="5000"
$env:NUM_CLIENTS="2"       # Max clients to wait for per round
$env:MIN_CLIENTS="2"       # Minimum clients required to proceed
python server.py
```

### 2. Run Clients

**Update the SERVER_IP in `client.py` first:**
```python
SERVER_IP = "192.168.107.136"  # Replace with your server's IP
```

**Then run clients (in separate terminals):**
```powershell
# Client 1
cd P:\CN_project\working
python client.py

# Client 2 (new terminal)
cd P:\CN_project\working
python client.py
```

### 3. Training Flow

- Server waits for up to `NUM_CLIENTS` (default: 2) per round
- Server requires at least `MIN_CLIENTS` (default: 2) to proceed
- If fewer than MIN_CLIENTS connect, the round is skipped
- After 3 rounds, the global model is saved to `global_model.pth`

## ⚙️ Configuration

### Server Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5000` | Server port |
| `NUM_CLIENTS` | `2` | Max clients per round |
| `MIN_CLIENTS` | `2` | Min clients to proceed |
| `rounds` | `3` | Number of training rounds |

### Client Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SERVER_IP` | `192.168.107.136` | Server IP address |
| `PORT` | `5000` | Server port |
| `timeout` | `120s` | Connection timeout |

## 🔍 How It Works

### Federated Learning Process:

1. **Server Initialization**
   - Creates a global model (SimpleNet)
   - Listens for client connections

2. **Training Round** (repeated 3 times)
   - Server waits for clients to connect
   - Sends global model to each client
   - Receives trained weights from clients
   - **Checks minimum threshold (2 clients)**
   - Aggregates weights using FedAvg algorithm
   - Updates global model

3. **Completion**
   - Saves final global model to disk

### Communication Protocol:

Both client and server use a **length-prefix protocol**:
1. Send 4 bytes indicating data length (big-endian)
2. Send the actual pickled data

This ensures reliable data transfer without connection closure ambiguity.

## 🐛 Common Issues & Solutions

### Issue: "Connection refused"
**Solution:** Make sure the server is running first, and the SERVER_IP in client.py matches your server's IP.

### Issue: "Only 1 clients participated, but 2 required"
**Solution:** This is expected behavior! Run at least 2 clients. The server will skip the round and wait for the next one.

### Issue: Client times out
**Solution:** 
- Check network connectivity
- Ensure firewall allows port 5000
- Increase timeout in server.py if training takes longer

### Issue: "Connection closed while receiving data"
**Solution:** This typically indicates a network interruption or the other end crashed. Check both server and client logs.

## 📊 Model Details

**SimpleNet Architecture:**
- Input: 10 features
- Output: 2 classes (binary classification)
- Single fully-connected layer

**Training Parameters:**
- Optimizer: SGD (lr=0.01)
- Loss: CrossEntropyLoss
- Local epochs: 5
- Batch: 50 samples (dummy data)

## 🔒 Security Note

⚠️ This is a **demonstration implementation**. For production use:
- Add authentication
- Encrypt communications (TLS/SSL)
- Validate model updates
- Add differential privacy
- Implement secure aggregation

## 📝 Example Output

### Server Output:
```
Server listening on 0.0.0.0:5000
Waiting for up to 2 clients per round
Minimum 2 clients required to proceed with each round

==================================================
Round 1/3
==================================================
[Round 1] Waiting for client 1/2...
[Round 1] Client 1/2 connected from ('192.168.107.136', 52431)
[Round 1] Sending global model to client 1...
[Round 1] Global model sent to client 1
[Round 1] Waiting for updates from client 1...
[Round 1] Received updates from client 1
[Round 1] Waiting for client 2/2...
[Round 1] Client 2/2 connected from ('192.168.107.136', 52432)
...
[Round 1] ✓ Global model updated with 2 client updates
```

### Client Output:
```
Connecting to server at 192.168.107.136:5000...
Connected to server.
Waiting to receive global model...
Expecting 1248 bytes of data...
Received 1248 bytes
Global model received and deserialized
Model loaded successfully
Starting local training...
  Epoch 1/5, Loss: 0.7234
  Epoch 5/5, Loss: 0.6891
Local training complete
Sending updated model back to server...
Sent 1248 bytes with 4-byte length prefix
Updated model sent successfully
Connection closed
```

## 📦 Dependencies

```bash
pip install torch
```

No additional dependencies required!

## 🤝 Contributing

Feel free to improve this implementation by:
- Adding more sophisticated models
- Implementing real datasets
- Adding metrics tracking
- Improving communication efficiency
- Adding security features

## 📄 License

This is a demonstration project for educational purposes.
