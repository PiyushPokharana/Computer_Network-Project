
import socket
import pickle
import torch
import os
from model_def import SimpleNet

SERVER_IP = os.environ.get("SERVER_IP", "192.168.2.32")
PORT = int(os.environ.get("SERVER_PORT", "5000"))

def local_train(model):
    """Simulate local training on dummy data"""
    x = torch.randn(50, 10)
    y = torch.randint(0, 2, (50,))
    loss_fn = torch.nn.CrossEntropyLoss()
    opt = torch.optim.SGD(model.parameters(), lr=0.01)

    for _ in range(5):
        opt.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        opt.step()
    return model.state_dict()

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

def main():
    client = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(30)  # 30 second timeout
        client.connect((SERVER_IP, PORT))
        print(f"Connected to server at {SERVER_IP}:{PORT}")

        # Receive global model
        print("Receiving global model...")
        recv_data = receive_data(client)
        global_state = pickle.loads(recv_data)
        model = SimpleNet()
        model.load_state_dict(global_state)
        print("Global model loaded successfully")

        # Perform local training
        print("Starting local training...")
        updated_state = local_train(model)
        print("Local training complete")

        # Send updated weights
        print("Sending updated model to server...")
        send_data(client, updated_state)
        print("Updated model sent successfully")
        
    except socket.timeout:
        print("ERROR: Connection timed out")
    except ConnectionError as e:
        print(f"ERROR: Connection error - {e}")
    except pickle.PickleError as e:
        print(f"ERROR: Serialization error - {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
    finally:
        if client:
            client.close()
            print("Connection closed")

if __name__ == "__main__":
    main()