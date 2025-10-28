import socket
import pickle
import torch
import os
import time
from model_def import SimpleNet

SERVER_IP = os.environ.get("SERVER_IP", "192.168.2.32")
PORT = int(os.environ.get("SERVER_PORT", "5000"))

class NetworkMetrics:
    """Track network performance metrics"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.bytes_sent = 0
        self.bytes_received = 0
        self.send_time = 0
        self.receive_time = 0
        self.connection_time = 0
        self.training_time = 0
        
    def get_bandwidth_mbps(self, bytes_transferred, time_taken):
        """Calculate bandwidth in Mbps"""
        if time_taken == 0:
            return 0
        return (bytes_transferred * 8) / (time_taken * 1_000_000)
    
    def print_summary(self):
        """Print network performance summary"""
        print(f"\n{'='*60}")
        print(f"NETWORK PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        print(f"  Data Sent:       {self.bytes_sent:,} bytes ({self.bytes_sent/1024:.2f} KB)")
        print(f"  Data Received:   {self.bytes_received:,} bytes ({self.bytes_received/1024:.2f} KB)")
        print(f"  Send Time:       {self.send_time:.3f} seconds")
        print(f"  Receive Time:    {self.receive_time:.3f} seconds")
        print(f"  Training Time:   {self.training_time:.3f} seconds")
        print(f"  Total Time:      {self.connection_time:.3f} seconds")
        print(f"  Upload Speed:    {self.get_bandwidth_mbps(self.bytes_sent, self.send_time):.2f} Mbps")
        print(f"  Download Speed:  {self.get_bandwidth_mbps(self.bytes_received, self.receive_time):.2f} Mbps")
        total_data = self.bytes_sent + self.bytes_received
        total_transfer_time = self.send_time + self.receive_time
        print(f"  Avg Throughput:  {self.get_bandwidth_mbps(total_data, total_transfer_time):.2f} Mbps")
        print(f"{'='*60}")

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

def receive_data(sock, metrics=None):
    """Receive data with length prefix and track metrics"""
    try:
        start_time = time.time()
        
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
        
        if metrics:
            metrics.receive_time = time.time() - start_time
            metrics.bytes_received = len(recv_data) + 4
        
        return recv_data
    except Exception as e:
        raise RuntimeError(f"Error receiving data: {e}")

def send_data(sock, data, metrics=None):
    """Send data with length prefix and track metrics"""
    try:
        start_time = time.time()
        
        data_bytes = pickle.dumps(data)
        length_bytes = len(data_bytes).to_bytes(4, 'big')
        sock.sendall(length_bytes + data_bytes)
        
        if metrics:
            metrics.send_time = time.time() - start_time
            metrics.bytes_sent = len(data_bytes) + 4
    except Exception as e:
        raise RuntimeError(f"Error sending data: {e}")

def main():
    client = None
    metrics = NetworkMetrics()
    
    try:
        conn_start = time.time()
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(120)  # 120 second timeout
        
        print(f"Connecting to server at {SERVER_IP}:{PORT}...")
        connect_start = time.time()
        client.connect((SERVER_IP, PORT))
        connect_time = (time.time() - connect_start) * 1000  # in ms
        print(f"Connected to server (connection time: {connect_time:.2f} ms)")

        # Respond to ping for latency measurement
        ping = client.recv(4)
        if ping == b'PING':
            client.send(b'PONG')

        # Receive global model
        print("Receiving global model...")
        recv_data = receive_data(client, metrics)
        global_state = pickle.loads(recv_data)
        model = SimpleNet()
        model.load_state_dict(global_state)
        print(f"Global model loaded successfully ({metrics.bytes_received/1024:.2f} KB received in {metrics.receive_time:.3f}s)")

        # Perform local training
        print("Starting local training...")
        train_start = time.time()
        updated_state = local_train(model)
        metrics.training_time = time.time() - train_start
        print(f"Local training complete ({metrics.training_time:.3f}s)")

        # Send updated weights
        print("Sending updated model to server...")
        send_data(client, updated_state, metrics)
        print(f"Updated model sent successfully ({metrics.bytes_sent/1024:.2f} KB sent in {metrics.send_time:.3f}s)")
        
        metrics.connection_time = time.time() - conn_start
        metrics.print_summary()
        
    except socket.timeout:
        print("ERROR: Connection timed out")
    except ConnectionError as e:
        print(f"ERROR: Connection error - {e}")
    except pickle.PickleError as e:
        print(f"ERROR: Serialization error - {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()
            print("Connection closed")

if __name__ == "__main__":
    main()
