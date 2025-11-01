# Implementation Guide - Priority 2 Features (Items 3-7)

This guide provides detailed, step-by-step instructions to implement the missing features.

---

## 📊 Item 3: Visualization and Monitoring

### Step 1: Create `visualize_training.py`

Create a new file to visualize training results:

```python
# visualize_training.py
import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

def load_training_history(filename='training_history.json'):
    """Load training history from JSON file"""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        print("Run the server first to generate training history.")
        return None
    
    with open(filename, 'r') as f:
        return json.load(f)

def plot_accuracy_and_loss(history):
    """Plot accuracy and loss curves"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    rounds = history['rounds']
    accuracies = history['accuracies']
    losses = history['losses']
    
    # Plot accuracy
    ax1.plot(rounds, accuracies, 'b-o', linewidth=2, markersize=8)
    ax1.set_xlabel('Round', fontsize=12)
    ax1.set_ylabel('Accuracy (%)', fontsize=12)
    ax1.set_title('Global Model Accuracy Over Rounds', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 100])
    
    # Add value labels on points
    for i, (r, acc) in enumerate(zip(rounds, accuracies)):
        ax1.annotate(f'{acc:.1f}%', (r, acc), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    # Plot loss
    ax2.plot(rounds, losses, 'r-o', linewidth=2, markersize=8)
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Loss', fontsize=12)
    ax2.set_title('Global Model Loss Over Rounds', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on points
    for i, (r, loss) in enumerate(zip(rounds, losses)):
        ax2.annotate(f'{loss:.3f}', (r, loss), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: training_curves.png")
    plt.show()

def plot_client_participation(history):
    """Plot number of clients per round"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    rounds = history['rounds']
    num_clients = history['num_clients']
    
    ax.bar(rounds, num_clients, color='green', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Number of Clients', fontsize=12)
    ax.set_title('Client Participation Per Round', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for r, nc in zip(rounds, num_clients):
        ax.text(r, nc + 0.1, str(nc), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('client_participation.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: client_participation.png")
    plt.show()

def plot_combined_metrics(history):
    """Create a comprehensive dashboard with all metrics"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    rounds = history['rounds']
    accuracies = history['accuracies']
    losses = history['losses']
    num_clients = history['num_clients']
    
    # 1. Accuracy over rounds (large plot)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(rounds, accuracies, 'b-o', linewidth=3, markersize=10, label='Accuracy')
    ax1.set_xlabel('Round', fontsize=12)
    ax1.set_ylabel('Accuracy (%)', fontsize=12)
    ax1.set_title('Global Model Accuracy Over Training Rounds', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 100])
    ax1.legend(fontsize=11)
    
    # 2. Loss over rounds
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(rounds, losses, 'r-o', linewidth=2, markersize=8)
    ax2.set_xlabel('Round', fontsize=11)
    ax2.set_ylabel('Loss', fontsize=11)
    ax2.set_title('Training Loss', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Client participation
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.bar(rounds, num_clients, color='green', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Round', fontsize=11)
    ax3.set_ylabel('Clients', fontsize=11)
    ax3.set_title('Client Participation', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Accuracy improvement per round
    ax4 = fig.add_subplot(gs[2, 0])
    acc_diff = [0] + [accuracies[i] - accuracies[i-1] for i in range(1, len(accuracies))]
    colors = ['green' if x >= 0 else 'red' for x in acc_diff]
    ax4.bar(rounds, acc_diff, color=colors, alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Round', fontsize=11)
    ax4.set_ylabel('Δ Accuracy (%)', fontsize=11)
    ax4.set_title('Accuracy Change Per Round', fontsize=13, fontweight='bold')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Summary statistics
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    
    stats_text = f"""
    Training Summary
    {'='*40}
    
    Total Rounds: {len(rounds)}
    
    Initial Accuracy: {accuracies[0]:.2f}%
    Final Accuracy: {accuracies[-1]:.2f}%
    Best Accuracy: {max(accuracies):.2f}%
    
    Initial Loss: {losses[0]:.4f}
    Final Loss: {losses[-1]:.4f}
    Best Loss: {min(losses):.4f}
    
    Avg Clients/Round: {sum(num_clients)/len(num_clients):.1f}
    Total Client Updates: {sum(num_clients)}
    
    Improvement: {accuracies[-1] - accuracies[0]:.2f}%
    """
    
    ax5.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', 
             facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Federated Learning Training Dashboard', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    plt.savefig('training_dashboard.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: training_dashboard.png")
    plt.show()

def print_summary(history):
    """Print text summary of training"""
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    
    print(f"\nTraining Timestamp: {history.get('timestamp', 'N/A')}")
    print(f"Total Rounds: {len(history['rounds'])}")
    
    accuracies = history['accuracies']
    losses = history['losses']
    
    print(f"\n📊 Accuracy Metrics:")
    print(f"  Initial:  {accuracies[0]:.2f}%")
    print(f"  Final:    {accuracies[-1]:.2f}%")
    print(f"  Best:     {max(accuracies):.2f}%")
    print(f"  Improvement: +{accuracies[-1] - accuracies[0]:.2f}%")
    
    print(f"\n📉 Loss Metrics:")
    print(f"  Initial:  {losses[0]:.4f}")
    print(f"  Final:    {losses[-1]:.4f}")
    print(f"  Best:     {min(losses):.4f}")
    print(f"  Reduction: -{losses[0] - losses[-1]:.4f}")
    
    print(f"\n👥 Client Participation:")
    print(f"  Average: {sum(history['num_clients'])/len(history['num_clients']):.1f}")
    print(f"  Total Updates: {sum(history['num_clients'])}")
    
    print("\n" + "="*60 + "\n")

def main():
    """Main function"""
    print("="*60)
    print("Federated Learning Training Visualization")
    print("="*60)
    
    # Load history
    history = load_training_history()
    if history is None:
        return
    
    print(f"\n✓ Loaded training history with {len(history['rounds'])} rounds\n")
    
    # Print summary
    print_summary(history)
    
    # Create visualizations
    print("Creating visualizations...")
    plot_combined_metrics(history)
    plot_accuracy_and_loss(history)
    plot_client_participation(history)
    
    print("\n✓ All visualizations created successfully!")
    print("\nGenerated files:")
    print("  - training_dashboard.png")
    print("  - training_curves.png")
    print("  - client_participation.png")

if __name__ == "__main__":
    main()
```

**How to use:**
```powershell
# After training completes, run:
python visualize_training.py
```

---

## 📈 Item 4: Visualization and Monitoring (Real-time Dashboard - Optional Advanced)

### Step 2: Create Real-Time Monitoring (Optional)

For a simple real-time monitor, create `monitor.py`:

```python
# monitor.py
import json
import time
import os
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_training(history_file='training_history.json', interval=2):
    """Monitor training progress in real-time"""
    print("Starting training monitor... (Press Ctrl+C to stop)")
    print("Waiting for training to start...\n")
    
    last_rounds = 0
    
    try:
        while True:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                current_rounds = len(history['rounds'])
                
                if current_rounds > last_rounds:
                    clear_screen()
                    print("="*70)
                    print("🔄 FEDERATED LEARNING TRAINING MONITOR")
                    print("="*70)
                    print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Monitoring: {history_file}")
                    print("="*70)
                    
                    if current_rounds > 0:
                        print(f"\n📊 Current Progress:")
                        print(f"  Round: {history['rounds'][-1]}")
                        print(f"  Accuracy: {history['accuracies'][-1]:.2f}%")
                        print(f"  Loss: {history['losses'][-1]:.4f}")
                        print(f"  Clients: {history['num_clients'][-1]}")
                        
                        if current_rounds > 1:
                            acc_change = history['accuracies'][-1] - history['accuracies'][-2]
                            loss_change = history['losses'][-1] - history['losses'][-2]
                            
                            print(f"\n📈 Change from Last Round:")
                            print(f"  Accuracy: {acc_change:+.2f}%")
                            print(f"  Loss: {loss_change:+.4f}")
                        
                        print(f"\n🏆 Best So Far:")
                        print(f"  Accuracy: {max(history['accuracies']):.2f}%")
                        print(f"  Loss: {min(history['losses']):.4f}")
                        
                        print(f"\n📝 Training History:")
                        print(f"{'Round':<10}{'Accuracy':<15}{'Loss':<15}{'Clients':<10}")
                        print("-"*50)
                        for i in range(len(history['rounds'])):
                            print(f"{history['rounds'][i]:<10}{history['accuracies'][i]:<15.2f}"
                                  f"{history['losses'][i]:<15.4f}{history['num_clients'][i]:<10}")
                    
                    last_rounds = current_rounds
                    print("\n" + "="*70)
                    print(f"Refreshing every {interval} seconds... (Ctrl+C to stop)")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print("\nRun 'python visualize_training.py' to generate charts!")

if __name__ == "__main__":
    import sys
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    monitor_training(interval=interval)
```

**How to use:**
```powershell
# In a separate terminal while training:
python monitor.py
```

---

## 📊 Item 5: Performance Metrics Collection

### Step 3: Add Metrics Collection to Server

Add these functions to `server.py`:

```python
# Add at the top with other imports
import sys

# Add this class after imports
class MetricsCollector:
    """Collect and track performance metrics"""
    def __init__(self):
        self.metrics = {
            'rounds': [],
            'round_start_times': [],
            'round_end_times': [],
            'round_durations': [],
            'bytes_sent': [],
            'bytes_received': [],
            'client_times': [],
            'aggregation_times': [],
            'evaluation_times': [],
            'network_overhead': []
        }
    
    def start_round(self, round_num):
        """Mark the start of a round"""
        self.current_round_start = time.time()
        self.current_bytes_sent = 0
        self.current_bytes_received = 0
        self.current_client_times = []
    
    def end_round(self, round_num):
        """Mark the end of a round"""
        duration = time.time() - self.current_round_start
        self.metrics['rounds'].append(round_num)
        self.metrics['round_start_times'].append(self.current_round_start)
        self.metrics['round_end_times'].append(time.time())
        self.metrics['round_durations'].append(duration)
        self.metrics['bytes_sent'].append(self.current_bytes_sent)
        self.metrics['bytes_received'].append(self.current_bytes_received)
        self.metrics['client_times'].append(self.current_client_times.copy())
        
        # Calculate network overhead (total bytes / round)
        total_bytes = self.current_bytes_sent + self.current_bytes_received
        self.metrics['network_overhead'].append(total_bytes)
    
    def record_send(self, num_bytes):
        """Record bytes sent"""
        self.current_bytes_sent += num_bytes
    
    def record_receive(self, num_bytes):
        """Record bytes received"""
        self.current_bytes_received += num_bytes
    
    def record_client_time(self, client_id, duration):
        """Record client processing time"""
        self.current_client_times.append({'client_id': client_id, 'duration': duration})
    
    def record_aggregation_time(self, duration):
        """Record aggregation time"""
        self.metrics['aggregation_times'].append(duration)
    
    def record_evaluation_time(self, duration):
        """Record evaluation time"""
        self.metrics['evaluation_times'].append(duration)
    
    def save_metrics(self, filename='performance_metrics.json'):
        """Save metrics to JSON file"""
        # Convert timestamps to readable format
        metrics_export = self.metrics.copy()
        metrics_export['round_start_times'] = [
            datetime.fromtimestamp(t).isoformat() 
            for t in self.metrics['round_start_times']
        ]
        metrics_export['round_end_times'] = [
            datetime.fromtimestamp(t).isoformat() 
            for t in self.metrics['round_end_times']
        ]
        
        with open(filename, 'w') as f:
            json.dump(metrics_export, f, indent=2)
        
        return filename
    
    def print_summary(self):
        """Print metrics summary"""
        if not self.metrics['rounds']:
            print("No metrics collected yet.")
            return
        
        print("\n" + "="*60)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*60)
        
        total_duration = sum(self.metrics['round_durations'])
        avg_duration = total_duration / len(self.metrics['round_durations'])
        
        total_sent = sum(self.metrics['bytes_sent'])
        total_received = sum(self.metrics['bytes_received'])
        total_bytes = total_sent + total_received
        
        print(f"\n⏱️  Timing Metrics:")
        print(f"  Total Training Time: {total_duration:.2f}s")
        print(f"  Avg Round Duration: {avg_duration:.2f}s")
        print(f"  Min Round Duration: {min(self.metrics['round_durations']):.2f}s")
        print(f"  Max Round Duration: {max(self.metrics['round_durations']):.2f}s")
        
        if self.metrics['aggregation_times']:
            print(f"  Avg Aggregation Time: {sum(self.metrics['aggregation_times'])/len(self.metrics['aggregation_times']):.2f}s")
        
        if self.metrics['evaluation_times']:
            print(f"  Avg Evaluation Time: {sum(self.metrics['evaluation_times'])/len(self.metrics['evaluation_times']):.2f}s")
        
        print(f"\n📡 Network Metrics:")
        print(f"  Total Data Sent: {total_sent/1024/1024:.2f} MB")
        print(f"  Total Data Received: {total_received/1024/1024:.2f} MB")
        print(f"  Total Network Traffic: {total_bytes/1024/1024:.2f} MB")
        print(f"  Avg Traffic/Round: {(total_bytes/len(self.metrics['rounds']))/1024/1024:.2f} MB")
        
        print("\n" + "="*60 + "\n")
```

Now update the `send_data` and `receive_data` functions to track bytes:

```python
# Modify send_data function
def send_data(sock, data, metrics=None):
    """Send data with length prefix"""
    try:
        data_bytes = pickle.dumps(data)
        data_bytes = simulate_network_conditions(data_bytes)
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        sock.sendall(length_bytes + data_bytes)
        
        total_sent = len(data_bytes) + 4
        print(f"Sent {total_sent} bytes with 4-byte length prefix")
        
        # Track metrics
        if metrics:
            metrics.record_send(total_sent)
        
    except Exception as e:
        raise RuntimeError(f"Error sending data: {e}")

# Modify receive_data function
def receive_data(sock, metrics=None):
    """Receive data with length prefix"""
    try:
        # Receive 4-byte length prefix
        length_bytes = b""
        while len(length_bytes) < 4:
            chunk = sock.recv(4 - len(length_bytes))
            if not chunk:
                raise ConnectionError("Connection closed while receiving length")
            length_bytes += chunk

        data_length = int.from_bytes(length_bytes, 'big')
        print(f"Expecting {data_length} bytes of data...")

        # Receive the actual data
        recv_data = b""
        while len(recv_data) < data_length:
            chunk = sock.recv(min(8192, data_length - len(recv_data)))
            if not chunk:
                raise ConnectionError("Connection closed while receiving data")
            recv_data += chunk

        total_received = len(recv_data) + 4
        print(f"Received {total_received} bytes")
        
        # Track metrics
        if metrics:
            metrics.record_receive(total_received)
        
        return simulate_network_conditions(recv_data)
    except Exception as e:
        raise RuntimeError(f"Error receiving data: {e}")
```

Update the `main()` function to use metrics:

```python
# In main(), after creating global_model, add:
metrics = MetricsCollector()

# In the round loop, add at the start:
metrics.start_round(r+1)

# Update send_data and receive_data calls:
send_data(conn, global_model.state_dict(), metrics)
recv_data = receive_data(conn, metrics)

# After aggregation, add:
agg_start = time.time()
new_state = aggregate_models(client_weights)
agg_time = time.time() - agg_start
metrics.record_aggregation_time(agg_time)

# After evaluation, add:
eval_start = time.time()
accuracy, avg_loss = evaluate_model(global_model)
eval_time = time.time() - eval_start
metrics.record_evaluation_time(eval_time)

# At the end of round:
metrics.end_round(r+1)

# After all rounds complete, add:
metrics.print_summary()
metrics_file = metrics.save_metrics()
print(f"✓ Performance metrics saved to '{metrics_file}'")
```

---

## 📊 Item 6: Advanced FL Techniques (FedProx)

### Step 4: Implement FedProx

Create a new file `fedprox.py`:

```python
# fedprox.py
"""
FedProx: Federated Optimization with Proximal Term
Helps handle heterogeneous clients better than FedAvg
"""
import torch
import torch.nn as nn

class FedProxOptimizer:
    """
    FedProx adds a proximal term to the local objective:
    min f(w) + (mu/2)||w - w_global||^2
    
    This helps keep local models closer to the global model.
    """
    def __init__(self, model, global_model, mu=0.01):
        """
        Args:
            model: Local model to train
            global_model: Global model (reference)
            mu: Proximal term coefficient (higher = stronger regularization)
        """
        self.model = model
        self.global_model = global_model
        self.mu = mu
    
    def calculate_proximal_term(self):
        """Calculate ||w - w_global||^2"""
        proximal_term = 0.0
        
        for name, param in self.model.named_parameters():
            global_param = dict(self.global_model.named_parameters())[name]
            proximal_term += torch.sum((param - global_param) ** 2)
        
        return (self.mu / 2.0) * proximal_term

def train_with_fedprox(model, global_model, train_loader, epochs=5, lr=0.01, mu=0.01):
    """
    Train local model using FedProx
    
    Args:
        model: Local model
        global_model: Global model (for proximal term)
        train_loader: Training data loader
        epochs: Number of local epochs
        lr: Learning rate
        mu: Proximal term coefficient
    
    Returns:
        Updated model state dict
    """
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    fedprox = FedProxOptimizer(model, global_model, mu=mu)
    
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0
        
        for data, target in train_loader:
            optimizer.zero_grad()
            
            # Forward pass
            output = model(data)
            
            # Standard loss
            loss = criterion(output, target)
            
            # Add proximal term
            proximal_loss = fedprox.calculate_proximal_term()
            total_loss_value = loss + proximal_loss
            
            # Backward and optimize
            total_loss_value.backward()
            optimizer.step()
            
            # Track metrics
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
        
        accuracy = 100. * correct / total
        avg_loss = total_loss / len(train_loader)
        print(f"  Epoch {epoch+1}/{epochs}: Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    return model.state_dict()
```

Update `client.py` to support FedProx:

```python
# Add at top of client.py:
from fedprox import train_with_fedprox

# Add environment variable for algorithm selection:
USE_FEDPROX = os.environ.get("USE_FEDPROX", "False").lower() == "true"
FEDPROX_MU = float(os.environ.get("FEDPROX_MU", "0.01"))

# In the training section, modify:
if USE_FEDPROX:
    print(f"Using FedProx (mu={FEDPROX_MU})")
    # Keep a copy of global model for proximal term
    global_model_copy = MNISTNet()
    global_model_copy.load_state_dict(global_weights)
    
    updated_weights = train_with_fedprox(
        model=local_model,
        global_model=global_model_copy,
        train_loader=train_loader,
        epochs=5,
        lr=0.01,
        mu=FEDPROX_MU
    )
else:
    print("Using standard FedAvg")
    # ... existing training code ...
```

---

## 🔄 Item 7: Client Selection Strategies

### Step 5: Implement Client Selection

Add to `server.py`:

```python
import random

class ClientSelector:
    """Strategies for selecting clients each round"""
    
    @staticmethod
    def select_all(num_clients):
        """Select all available clients"""
        return list(range(num_clients))
    
    @staticmethod
    def select_random(num_clients, fraction=0.5):
        """
        Randomly select a fraction of clients
        
        Args:
            num_clients: Total number of clients
            fraction: Fraction of clients to select (0-1)
        
        Returns:
            List of selected client indices
        """
        num_selected = max(1, int(num_clients * fraction))
        return random.sample(range(num_clients), num_selected)
    
    @staticmethod
    def select_importance_based(client_metrics, top_k=None):
        """
        Select clients based on importance (e.g., data size, loss)
        
        Args:
            client_metrics: Dict of {client_id: metric_value}
            top_k: Number of top clients to select
        
        Returns:
            List of selected client indices
        """
        if top_k is None:
            top_k = len(client_metrics) // 2
        
        # Sort by metric (higher is better)
        sorted_clients = sorted(client_metrics.items(), 
                               key=lambda x: x[1], 
                               reverse=True)
        
        return [client_id for client_id, _ in sorted_clients[:top_k]]
    
    @staticmethod
    def select_round_robin(num_clients, round_num, clients_per_round):
        """
        Select clients in round-robin fashion
        
        Args:
            num_clients: Total number of clients
            round_num: Current round number
            clients_per_round: Number of clients per round
        
        Returns:
            List of selected client indices
        """
        start_idx = (round_num * clients_per_round) % num_clients
        selected = []
        
        for i in range(clients_per_round):
            idx = (start_idx + i) % num_clients
            selected.append(idx)
        
        return selected

# Add configuration
SELECTION_STRATEGY = os.environ.get("CLIENT_SELECTION", "all")  # all, random, importance, roundrobin
SELECTION_FRACTION = float(os.environ.get("SELECTION_FRACTION", "1.0"))

# In main(), before the round loop:
selector = ClientSelector()

# In the round loop, modify client selection:
if SELECTION_STRATEGY == "random":
    selected_clients = selector.select_random(NUM_CLIENTS, SELECTION_FRACTION)
    print(f"[Round {r+1}] Selected {len(selected_clients)} clients: {selected_clients}")
elif SELECTION_STRATEGY == "roundrobin":
    clients_per_round = max(1, int(NUM_CLIENTS * SELECTION_FRACTION))
    selected_clients = selector.select_round_robin(NUM_CLIENTS, r, clients_per_round)
    print(f"[Round {r+1}] Selected clients (round-robin): {selected_clients}")
else:
    selected_clients = selector.select_all(NUM_CLIENTS)

# Modify the client loop to only process selected clients:
for i in selected_clients:
    # ... existing client handling code ...
```

---

## 🎯 Quick Implementation Checklist

### Immediate Actions (Today):

1. ✅ **Create visualize_training.py**
   ```powershell
   # Copy the code above into the file
   # Test it (if you have training_history.json):
   python visualize_training.py
   ```

2. ✅ **Create monitor.py**
   ```powershell
   # Copy the code above
   # Test in separate terminal during training:
   python monitor.py
   ```

3. ✅ **Add MetricsCollector to server.py**
   - Copy the MetricsCollector class
   - Update send_data/receive_data functions
   - Update main() to use metrics
   - Test and verify metrics are saved

4. ✅ **Create fedprox.py**
   ```powershell
   # Copy the code above
   # Update client.py to support it
   # Test with: $env:USE_FEDPROX="True"; python client.py
   ```

5. ✅ **Add ClientSelector to server.py**
   - Copy the ClientSelector class
   - Update server main() to use selection strategies
   - Test with: $env:CLIENT_SELECTION="random"; python server.py

### Testing (After Implementation):

```powershell
# Terminal 1 - Start monitoring
python monitor.py

# Terminal 2 - Start server with metrics
python server.py

# Terminal 3 - Start client 1
$env:CLIENT_ID="0"; python client.py

# Terminal 4 - Start client 2
$env:CLIENT_ID="1"; python client.py

# After training completes:
python visualize_training.py
```

---

## 📊 Expected Outputs

After implementation, you'll have:

1. **training_dashboard.png** - Comprehensive training visualization
2. **training_curves.png** - Accuracy and loss plots
3. **client_participation.png** - Client participation bar chart
4. **performance_metrics.json** - Detailed performance data
5. **Real-time monitor** - Live training progress in terminal
6. **FedProx support** - Better handling of heterogeneous clients
7. **Client selection** - Flexible client selection strategies

---

## 🚀 Next Steps After Implementation

1. Run experiments with different configurations
2. Compare FedAvg vs FedProx
3. Test different client selection strategies
4. Generate comprehensive results
5. Create comparison charts
6. Document findings

