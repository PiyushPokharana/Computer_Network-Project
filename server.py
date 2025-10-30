import socket
import pickle
import torch
import os
import json
from datetime import datetime
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from model_def import MNISTNet

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "5000"))
NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))
MIN_CLIENTS = int(os.environ.get("MIN_CLIENTS", "2"))  # Minimum clients required per round

def receive_data(sock):
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
        
        # Receive the actual data
        recv_data = b""
        while len(recv_data) < data_length:
            chunk = sock.recv(min(8192, data_length - len(recv_data)))
            if not chunk:
                raise ConnectionError("Connection closed while receiving data")
            recv_data += chunk
        
        return recv_data
    except Exception as e:
        raise RuntimeError(f"Error receiving data: {e}")

def send_data(sock, data):
    """Send data with length prefix"""
    try:
        data_bytes = pickle.dumps(data)
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        sock.sendall(length_bytes + data_bytes)
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
                    send_data(conn, global_model.state_dict())
                    print(f"[Round {r+1}] Global model sent to client {i+1}")

                    # Receive updated weights
                    print(f"[Round {r+1}] Waiting for updates from client {i+1}...")
                    recv_data = receive_data(conn)
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
                new_state = aggregate_models(client_weights)
                global_model.load_state_dict(new_state)
                print(f"[Round {r+1}] ✓ Global model updated with {num_clients_received} client updates")
                
                # Evaluate model
                accuracy, avg_loss = evaluate_model(global_model)
                
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

        # Save final model and training history
        print("\n" + "="*60)
        print("Training complete!")
        print("="*60)
        
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