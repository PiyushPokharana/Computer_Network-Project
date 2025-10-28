import socket
import pickle
import torch
from model_def import SimpleNet

SERVER_IP = "192.168.2.32"   # Replace with actual server IP
PORT = 5000

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
        return recv_data
    except Exception as e:
        raise RuntimeError(f"Error receiving data: {e}")

def send_data(sock, data):
    """Send data with length prefix (matching server protocol)"""
    try:
        data_bytes = pickle.dumps(data)
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        sock.sendall(length_bytes + data_bytes)
        print(f"Sent {len(data_bytes)} bytes with 4-byte length prefix")
    except Exception as e:
        raise RuntimeError(f"Error sending data: {e}")

def local_train(model):
    """Simulate local training on dummy data"""
    print("Starting local training...")
    x = torch.randn(50, 10)
    y = torch.randint(0, 2, (50,))
    loss_fn = torch.nn.CrossEntropyLoss()
    opt = torch.optim.SGD(model.parameters(), lr=0.01)

    for epoch in range(5):
        opt.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        opt.step()
        if epoch == 0 or epoch == 4:
            print(f"  Epoch {epoch+1}/5, Loss: {loss.item():.4f}")
    
    print("Local training complete")
    return model.state_dict()

def main():
    client = None
    try:
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
        
        model = SimpleNet()
        model.load_state_dict(global_state)
        print("Model loaded successfully")

        # Perform local training
        updated_state = local_train(model)

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
    finally:
        if client:
            client.close()
            print("Connection closed")

if __name__ == "__main__":
    main()
