# 🚀 Step-by-Step Guide to Run Federated Learning

## Prerequisites ✅
- ✅ Virtual environment activated (venv)
- ✅ All packages installed
- ✅ All implementation tests passed

---

## 🎯 Quick Test (Single Machine - Localhost)

### Method 1: Using PowerShell Terminals (Recommended for Testing)

#### **Step 1: Start the Server**

Open your **first terminal** and run:

```powershell
# Set environment to use localhost for testing
$env:SERVER_HOST="127.0.0.1"
$env:SERVER_PORT="5000"
$env:NUM_CLIENTS="2"

# Start the server
python server.py
```

**What you'll see:**
- Server starts and shows network architecture
- Model parameters summary
- Waiting for 2 clients...

**⚠️ Keep this terminal running!**

---

#### **Step 2: Start Client 1**

Open a **second terminal** and run:

```powershell
# Set environment for Client 1
$env:SERVER_IP="127.0.0.1"
$env:SERVER_PORT="5000"
$env:CLIENT_ID="0"
$env:NUM_CLIENTS="2"

# Start client 1
python client.py
```

**What you'll see:**
- Client connects to server
- Downloads global model
- Trains locally on its data partition
- Sends updates back to server

**⚠️ Keep this terminal running!**

---

#### **Step 3: Start Client 2**

Open a **third terminal** and run:

```powershell
# Set environment for Client 2
$env:SERVER_IP="127.0.0.1"
$env:SERVER_PORT="5000"
$env:CLIENT_ID="1"
$env:NUM_CLIENTS="2"

# Start client 2
python client.py
```

**What you'll see:**
- Client 2 connects and trains
- Server aggregates both clients' updates
- Round 1 completes!
- Process repeats for remaining rounds

---

#### **Step 4: Monitor Training (Optional - Run Before Step 1)**

Open a **fourth terminal** (before starting server) and run:

```powershell
# Start real-time monitor
python monitor.py
```

**What you'll see:**
- Live updates every 2 seconds
- Current round, accuracy, loss
- Historical data table
- Auto-refreshes as training progresses

---

#### **Step 5: Visualize Results**

After training completes, run:

```powershell
# Generate all visualizations
python visualize_all.py
```

**What you'll get:**
- `complete_dashboard.png` - Comprehensive overview
- Training metrics, performance metrics, all in one!

**Or generate individual visualizations:**

```powershell
# Training curves only
python visualize_training.py

# Performance metrics only
python visualize_metrics.py
```

---

## 🖥️ Multi-Machine Setup (Real Network)

### For Running on Multiple Laptops/PCs

#### **On the Server Machine:**

1. Find your IP address:
```powershell
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.10)
```

2. Start the server:
```powershell
# Replace with your actual IP
$env:SERVER_HOST="192.168.1.10"  # Your IP here
$env:SERVER_PORT="5000"
$env:NUM_CLIENTS="2"

python server.py
```

#### **On Each Client Machine:**

1. Run the client:
```powershell
# Replace with server's IP
$env:SERVER_IP="192.168.1.10"  # Server's IP here
$env:SERVER_PORT="5000"
$env:CLIENT_ID="0"  # Change to 1, 2, 3... for each client

python client.py
```

---

## 📁 Expected Outputs

After a successful training session, you'll have:

### Data Files:
```
training_history.json           # Training metrics
performance_metrics.json        # Performance data
param_snapshot_round_0.json     # Initial parameters
param_snapshot_round_1.json     # Round 1 parameters
param_snapshot_round_2.json     # Round 2 parameters
...
global_model.pth               # Final trained model
```

### Visualization Files:
```
complete_dashboard.png         # All-in-one dashboard
training_dashboard.png         # Training metrics
training_curves.png            # Accuracy/loss plots
client_participation.png       # Client stats
performance_metrics.png        # Performance charts
```

---

## 🔧 Common Issues & Solutions

### Issue 1: "Address already in use"
**Solution:**
```powershell
# Change the port
$env:SERVER_PORT="5001"
```

### Issue 2: "Connection refused"
**Solutions:**
1. Check server is running first
2. Verify PORT numbers match (both use 5000)
3. Check IP address is correct
4. Check firewall isn't blocking

### Issue 3: "Timeout waiting for client"
**Solutions:**
1. Start clients within 2 minutes of server starting
2. Check network connectivity
3. Verify IP and PORT are correct

### Issue 4: "Module not found"
**Solutions:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install missing packages
pip install torch torchvision matplotlib numpy tabulate
```

---

## 🎬 Complete Example Session

Here's what a complete run looks like:

### Terminal 1 (Monitor - Optional):
```powershell
python monitor.py
# Shows: Waiting for training to start...
```

### Terminal 2 (Server):
```powershell
$env:SERVER_HOST="127.0.0.1"; $env:SERVER_PORT="5000"; $env:NUM_CLIENTS="2"
python server.py
# Shows: Server listening on 127.0.0.1:5000
# Shows: Waiting for up to 2 clients per round
```

### Terminal 3 (Client 1):
```powershell
$env:SERVER_IP="127.0.0.1"; $env:SERVER_PORT="5000"; $env:CLIENT_ID="0"
python client.py
# Shows: Connecting to server...
# Shows: Training on local data...
# Shows: Sending updates to server...
```

### Terminal 4 (Client 2):
```powershell
$env:SERVER_IP="127.0.0.1"; $env:SERVER_PORT="5000"; $env:CLIENT_ID="1"
python client.py
# Shows: Same process as Client 1
```

### After Training (Terminal 5):
```powershell
python visualize_all.py
# Shows: Creating comprehensive dashboard...
# Shows: ✓ Saved: complete_dashboard.png
# Opens the visualization
```

---

## 📊 What to Expect

### Training Time:
- **2 clients, 5 rounds**: ~2-5 minutes
- **2 clients, 10 rounds**: ~5-10 minutes
- Depends on: CPU speed, dataset size, network conditions

### Accuracy:
- **Initial**: ~10-20% (random guessing)
- **After 5 rounds**: ~80-90%
- **After 10 rounds**: ~90-95%

### Files Generated:
- 7-10 JSON files (history + snapshots)
- 5 PNG visualization files
- 1 model file (.pth)

---

## 🎯 Quick Commands Reference

### Single-Line Commands (Easy Copy-Paste):

**Start Server:**
```powershell
$env:SERVER_HOST="127.0.0.1"; $env:SERVER_PORT="5000"; $env:NUM_CLIENTS="2"; python server.py
```

**Start Client 1:**
```powershell
$env:SERVER_IP="127.0.0.1"; $env:SERVER_PORT="5000"; $env:CLIENT_ID="0"; python client.py
```

**Start Client 2:**
```powershell
$env:SERVER_IP="127.0.0.1"; $env:SERVER_PORT="5000"; $env:CLIENT_ID="1"; python client.py
```

**Monitor Training:**
```powershell
python monitor.py
```

**Visualize All:**
```powershell
python visualize_all.py
```

---

## 💡 Pro Tips

1. **Always start monitor first** - It's helpful to see progress
2. **Start server before clients** - Clients can't connect to non-existent server
3. **Use localhost for testing** - Use 127.0.0.1 for single-machine testing
4. **Check the monitor** - It shows if training is progressing
5. **Wait for completion** - Let all rounds finish before visualizing
6. **Save your results** - Move generated files to a results folder
7. **Take screenshots** - Capture the monitor and visualizations for your report

---

## 🎉 Success Indicators

You'll know it's working when you see:

✅ Server shows "Client connected"
✅ Clients show "Training complete" after each round
✅ Monitor shows increasing accuracy
✅ No error messages in any terminal
✅ JSON files are created in the directory
✅ PNG files are generated after visualization

---

## 🆘 Need Help?

If something goes wrong:

1. **Check all terminals** - Look for error messages
2. **Verify environment variables** - Use `$env:VARIABLE_NAME` to check
3. **Run test_implementation.py** - Verify everything is set up
4. **Check the logs** - Server and clients show detailed logs
5. **Review this guide** - Follow steps exactly

---

## 📚 Next Steps

After successful run:

1. ✅ Check generated PNG files
2. ✅ Review training_history.json
3. ✅ Review performance_metrics.json
4. ✅ Include visualizations in your report
5. ✅ Run multiple experiments with different settings
6. ✅ Compare results

---

**Happy Training! 🚀**
