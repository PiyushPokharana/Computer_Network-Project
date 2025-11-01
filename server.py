import socket
import pickle
import torch
import os
import json
import random
import time
from datetime import datetime
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from model_def import MNISTNet

HOST = os.environ.get("SERVER_HOST", "192.168.109.142")
PORT = int(os.environ.get("SERVER_PORT", "5000"))
NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))
MIN_CLIENTS = int(os.environ.get("MIN_CLIENTS", "2"))  # Minimum clients required per round

# Define 6G network simulation parameters
BANDWIDTH = 1000  # in Mbps
LATENCY = 10  # in ms
JITTER = 5  # in ms
PACKET_LOSS = 0.01  # 1% packet loss

def simulate_network_conditions(data):
    """Simulate 6G network conditions on the data transfer."""
    # Simulate latency
    simulated_latency = LATENCY + random.uniform(-JITTER, JITTER)
    time.sleep(simulated_latency / 1000)  # Convert ms to seconds

    # Simulate packet loss
    if random.random() < PACKET_LOSS:
        raise ConnectionError("Simulated packet loss occurred")

    # Simulate bandwidth limitation
    data_size = len(data) * 8  # Convert bytes to bits
    transfer_time = data_size / (BANDWIDTH * 1e6)  # Bandwidth in bits per second
    time.sleep(transfer_time)

    return data

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
        
        return simulate_network_conditions(recv_data)  # Simulate network conditions
    except Exception as e:
        raise RuntimeError(f"Error receiving data: {e}")

def send_data(sock, data, metrics=None):
    """Send data with length prefix"""
    try:
        data_bytes = pickle.dumps(data)
        data_bytes = simulate_network_conditions(data_bytes)  # Simulate network conditions
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        sock.sendall(length_bytes + data_bytes)
        
        total_sent = len(data_bytes) + 4
        print(f"Sent {total_sent} bytes with 4-byte length prefix")
        
        # Track metrics
        if metrics:
            metrics.record_send(total_sent)
            
    except Exception as e:
        raise RuntimeError(f"Error sending data: {e}")

def aggregate_models(client_weights):
    """Average model weights from all clients"""
    if not client_weights:
        raise ValueError("No client weights to aggregate")
    
    new_state = {}
    for key in client_weights[0].keys():
        new_state[key] = sum([w[key] for w in client_weights]) / len(client_weights)
    return new_state

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
        self.current_round_start = None
        self.current_bytes_sent = 0
        self.current_bytes_received = 0
        self.current_client_times = []
    
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
        
        total_bytes = self.current_bytes_sent + self.current_bytes_received
        self.metrics['network_overhead'].append(total_bytes)
    
    def record_send(self, num_bytes):
        """Record bytes sent"""
        self.current_bytes_sent += num_bytes
    
    def record_receive(self, num_bytes):
        """Record bytes received"""
        self.current_bytes_received += num_bytes
    
    def record_aggregation_time(self, duration):
        """Record aggregation time"""
        self.metrics['aggregation_times'].append(duration)
    
    def record_evaluation_time(self, duration):
        """Record evaluation time"""
        self.metrics['evaluation_times'].append(duration)
    
    def save_metrics(self, filename='performance_metrics.json'):
        """Save metrics to JSON file"""
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

def print_network_architecture(model):
    """Display network architecture in a visual format"""
    print(f"\n{'='*60}")
    print("Network Architecture")
    print(f"{'='*60}")
    print("\nModel Structure:")
    print(model)
    print(f"{'='*60}\n")

def print_model_parameters(model, detailed=False):
    """Display model architecture and parameters"""
    print(f"\n{'='*60}")
    print("Model Parameters Summary")
    print(f"{'='*60}")
    
    total_params = 0
    trainable_params = 0
    
    print(f"\n{'Layer':<20} {'Type':<20} {'Parameters':<15} {'Shape':<30}")
    print("-" * 85)
    
    for name, param in model.named_parameters():
        num_params = param.numel()
        total_params += num_params
        if param.requires_grad:
            trainable_params += num_params
        
        param_shape = str(list(param.shape))
        layer_type = name.split('.')[-1]  # Get parameter type (weight/bias)
        
        print(f"{name:<20} {layer_type:<20} {num_params:<15,} {param_shape:<30}")
        
        # Show parameter statistics
        if detailed:
            print(f"  ├─ Mean: {param.data.mean():.6f}, Std: {param.data.std():.6f}")
            print(f"  ├─ Min: {param.data.min():.6f}, Max: {param.data.max():.6f}")
            print(f"  └─ Grad: {'Enabled' if param.requires_grad else 'Disabled'}")
    
    print("-" * 85)
    print(f"{'Total Parameters:':<35} {total_params:,}")
    print(f"{'Trainable Parameters:':<35} {trainable_params:,}")
    print(f"{'Non-trainable Parameters:':<35} {total_params - trainable_params:,}")
    print(f"{'Model Size (MB):':<35} {total_params * 4 / (1024**2):.2f}")  # Assuming float32
    print(f"{'='*60}\n")

def save_parameter_snapshot(model, round_num, filename_prefix="param_snapshot"):
    """Save parameter values to a JSON file for analysis"""
    param_data = {}
    for name, param in model.named_parameters():
        param_data[name] = {
            'shape': list(param.shape),
            'mean': float(param.data.mean()),
            'std': float(param.data.std()),
            'min': float(param.data.min()),
            'max': float(param.data.max()),
            'requires_grad': param.requires_grad
        }
    
    filename = f"{filename_prefix}_round_{round_num}.json"
    with open(filename, 'w') as f:
        json.dump(param_data, f, indent=2)
    
    return filename

def evaluate_model(model):
    """Evaluate global model on MNIST test set"""
    print("Evaluating model on test set...")
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    model.eval()
    correct = 0
    total = 0
    test_loss = 0
    loss_fn = torch.nn.CrossEntropyLoss()
    
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            test_loss += loss_fn(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
    
    accuracy = 100. * correct / total
    avg_loss = test_loss / len(test_loader)
    
    print(f"Test Set: Average loss: {avg_loss:.4f}, Accuracy: {correct}/{total} ({accuracy:.2f}%)")
    
    return accuracy, avg_loss

def main():
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Enable address reuse to avoid 'Address already in use' errors
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(NUM_CLIENTS)
        print(f"{'='*60}")
        print(f"Federated Learning Server - MNIST Classification")
        print(f"{'='*60}")
        print(f"Server listening on {HOST}:{PORT}")
        print(f"Waiting for up to {NUM_CLIENTS} clients per round")
        print(f"Minimum {MIN_CLIENTS} clients required to proceed with each round")
        print(f"{'='*60}\n")

        global_model = MNISTNet()
        
        # Display network architecture
        print_network_architecture(global_model)
        
        # Display initial model parameters
        print_model_parameters(global_model, detailed=True)
        
        # Save initial parameter snapshot
        snapshot_file = save_parameter_snapshot(global_model, 0)
        print(f"✓ Initial parameter snapshot saved to '{snapshot_file}'")
        
        # Initialize metrics collector
        metrics = MetricsCollector()
        print("✓ Performance metrics tracking enabled\n")
        
        rounds = 5  # Increased rounds for better training
        
        # Training history for visualization
        training_history = {
            'rounds': [],
            'accuracies': [],
            'losses': [],
            'num_clients': [],
            'timestamp': datetime.now().isoformat()
        }

        for r in range(rounds):
            print(f"\n{'='*60}")
            print(f"Round {r+1}/{rounds}")
            print(f"{'='*60}")
            
            # Start metrics collection for this round
            metrics.start_round(r+1)
            
            client_weights = []

            for i in range(NUM_CLIENTS):
                conn = None
                try:
                    print(f"[Round {r+1}] Waiting for client {i+1}/{NUM_CLIENTS}...")
                    conn, addr = server.accept()
                    conn.settimeout(120)  # 2 minute timeout per client
                    print(f"[Round {r+1}] Client {i+1}/{NUM_CLIENTS} connected from {addr}")

                    # Send global model
                    print(f"[Round {r+1}] Sending global model to client {i+1}...")
                    send_data(conn, global_model.state_dict(), metrics)
                    print(f"[Round {r+1}] Global model sent to client {i+1}")

                    # Receive updated weights
                    print(f"[Round {r+1}] Waiting for updates from client {i+1}...")
                    recv_data = receive_data(conn, metrics)
                    updated_weights = pickle.loads(recv_data)
                    client_weights.append(updated_weights)
                    print(f"[Round {r+1}] Received updates from client {i+1}")
                    
                except socket.timeout:
                    print(f"ERROR: Client {i+1} timed out")
                except Exception as e:
                    print(f"ERROR: Failed to process client {i+1}: {e}")
                finally:
                    if conn:
                        conn.close()

            # Check minimum client threshold
            num_clients_received = len(client_weights)
            print(f"\n[Round {r+1}] Received updates from {num_clients_received}/{NUM_CLIENTS} clients")
            
            if num_clients_received < MIN_CLIENTS:
                print(f"WARNING: Only {num_clients_received} clients participated, but {MIN_CLIENTS} required.")
                print(f"Skipping aggregation for round {r+1}. Global model unchanged.")
                continue
            
            # Aggregate updates
            try:
                agg_start = time.time()
                new_state = aggregate_models(client_weights)
                global_model.load_state_dict(new_state)
                agg_time = time.time() - agg_start
                metrics.record_aggregation_time(agg_time)
                print(f"[Round {r+1}] ✓ Global model updated with {num_clients_received} client updates (took {agg_time:.2f}s)")
                
                # Display parameter statistics after aggregation
                print(f"\n[Round {r+1}] Parameter Statistics After Aggregation:")
                print("-" * 60)
                for name, param in global_model.named_parameters():
                    print(f"{name:<20} Mean: {param.data.mean():.6f}, Std: {param.data.std():.6f}, "
                          f"Min: {param.data.min():.6f}, Max: {param.data.max():.6f}")
                print("-" * 60)
                
                # Save parameter snapshot for this round
                snapshot_file = save_parameter_snapshot(global_model, r+1)
                print(f"✓ Parameter snapshot saved to '{snapshot_file}'")
                
                # Evaluate model
                eval_start = time.time()
                accuracy, avg_loss = evaluate_model(global_model)
                eval_time = time.time() - eval_start
                metrics.record_evaluation_time(eval_time)
                
                # Save history
                training_history['rounds'].append(r+1)
                training_history['accuracies'].append(accuracy)
                training_history['losses'].append(avg_loss)
                training_history['num_clients'].append(num_clients_received)
                
                print(f"[Round {r+1}] ✓ Accuracy: {accuracy:.2f}%, Loss: {avg_loss:.4f}")
                
            except Exception as e:
                print(f"ERROR: Failed to aggregate models: {e}")
                import traceback
                traceback.print_exc()
            
            # End metrics collection for this round
            metrics.end_round(r+1)

        # Save final model and training history
        print("\n" + "="*60)
        print("Training complete!")
        print("="*60)
        
        # Print and save performance metrics
        metrics.print_summary()
        metrics_file = metrics.save_metrics()
        print(f"✓ Performance metrics saved to '{metrics_file}'")
        
        # Save model
        torch.save(global_model.state_dict(), "global_model.pth")
        print("✓ Global model saved to 'global_model.pth'")
        
        # Save training history
        with open('training_history.json', 'w') as f:
            json.dump(training_history, f, indent=2)
        print("✓ Training history saved to 'training_history.json'")
        
        # Print final results
        if training_history['accuracies']:
            print(f"\nFinal Results:")
            print(f"  Best Accuracy: {max(training_history['accuracies']):.2f}%")
            print(f"  Final Accuracy: {training_history['accuracies'][-1]:.2f}%")
            print(f"  Total Rounds: {len(training_history['rounds'])}")
        
        print("\nRun 'python visualize_training.py' to see training curves!")
        print("Run 'python visualize_metrics.py' to see performance metrics!")
        
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    except Exception as e:
        print(f"ERROR: Server error - {e}")
        import traceback
        traceback.print_exc()
    finally:
        if server:
            server.close()
            print("Server socket closed")

if __name__ == "__main__":
    main()