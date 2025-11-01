import socket
import pickle
import torch
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import os
from model_def import MNISTNet
import random
import time

SERVER_IP = os.environ.get("SERVER_IP", "192.168.109.142")   # Server IP (configurable via env)
PORT = int(os.environ.get("SERVER_PORT", "5000"))  # Should match server port

# Get client ID from environment or default to 0
CLIENT_ID = int(os.environ.get("CLIENT_ID", "0"))
NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))

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

def receive_data(sock):
    """Receive data with length prefix (matching server protocol)"""
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
        
        print(f"Received {len(recv_data)} bytes")
        return simulate_network_conditions(recv_data)  # Simulate network conditions
    except Exception as e:
        raise RuntimeError(f"Error receiving data: {e}")

def send_data(sock, data):
    """Send data with length prefix (matching server protocol)"""
    try:
        data_bytes = pickle.dumps(data)
        data_bytes = simulate_network_conditions(data_bytes)  # Simulate network conditions
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        sock.sendall(length_bytes + data_bytes)
        print(f"Sent {len(data_bytes)} bytes with 4-byte length prefix")
    except Exception as e:
        raise RuntimeError(f"Error sending data: {e}")

def load_mnist_client_data(client_id, num_clients=2):
    """Load MNIST data for this specific client"""
    print(f"Loading MNIST data for client {client_id}/{num_clients-1}...")
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Download MNIST if needed
    dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    
    # Divide data among clients (simple split - each gets equal portion)
    total_samples = len(dataset)
    samples_per_client = total_samples // num_clients
    start_idx = client_id * samples_per_client
    end_idx = start_idx + samples_per_client if client_id < num_clients - 1 else total_samples
    
    # Create subset for this client
    indices = list(range(start_idx, end_idx))
    client_dataset = Subset(dataset, indices)
    
    print(f"Client {client_id} has {len(client_dataset)} samples (indices {start_idx}-{end_idx-1})")
    
    return DataLoader(client_dataset, batch_size=32, shuffle=True)

def local_train(model, client_id, epochs=5):
    """Train model on local MNIST data"""
    print(f"Starting local training for client {client_id}...")
    dataloader = load_mnist_client_data(client_id, NUM_CLIENTS)
    
    loss_fn = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(dataloader):
            optimizer.zero_grad()
            output = model(data)
            loss = loss_fn(output, target)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
        
        accuracy = 100. * correct / total
        avg_loss = epoch_loss / len(dataloader)
        print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    print("Local training complete")
    return model.state_dict()

def main():
    client = None
    try:
        print(f"=== Federated Learning Client {CLIENT_ID} ===")
        print(f"Connecting to server at {SERVER_IP}:{PORT}...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(120)  # 2 minute timeout
        client.connect((SERVER_IP, PORT))
        print("Connected to server.")

        # Receive global model
        print("Waiting to receive global model...")
        recv_data = receive_data(client)
        global_state = pickle.loads(recv_data)
        print("Global model received and deserialized")
        
        model = MNISTNet()
        model.load_state_dict(global_state)
        print("Model loaded successfully")

        # Perform local training
        updated_state = local_train(model, CLIENT_ID)

        # Send updated weights
        print("Sending updated model back to server...")
        send_data(client, updated_state)
        print("Updated model sent successfully")
        
    except socket.timeout:
        print("ERROR: Connection timed out")
    except ConnectionRefusedError:
        print(f"ERROR: Could not connect to server at {SERVER_IP}:{PORT}")
        print("Make sure the server is running and the IP/PORT are correct")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()
            print("Connection closed")

if __name__ == "__main__":
    main()
