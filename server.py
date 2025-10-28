import socket
import pickle
import torch
import os
import time
import threading
from model_def import SimpleNet

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "5000"))
NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))

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
        
    def get_bandwidth_mbps(self, bytes_transferred, time_taken):
        """Calculate bandwidth in Mbps"""
        if time_taken == 0:
            return 0
        return (bytes_transferred * 8) / (time_taken * 1_000_000)
    
    def print_summary(self, client_id, round_num):
        """Print network performance summary"""
        print(f"\n--- Network Metrics: Client {client_id} (Round {round_num}) ---")
        print(f"  Data Sent:     {self.bytes_sent:,} bytes ({self.bytes_sent/1024:.2f} KB)")
        print(f"  Data Received: {self.bytes_received:,} bytes ({self.bytes_received/1024:.2f} KB)")
        print(f"  Send Time:     {self.send_time:.3f} seconds")
        print(f"  Receive Time:  {self.receive_time:.3f} seconds")
        print(f"  Upload Speed:  {self.get_bandwidth_mbps(self.bytes_sent, self.send_time):.2f} Mbps")
        print(f"  Download Speed: {self.get_bandwidth_mbps(self.bytes_received, self.receive_time):.2f} Mbps")
        print(f"  Total Latency: {self.connection_time:.3f} seconds")
        print(f"-" * 60)

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

def aggregate_models(client_weights):
    """Average model weights from all clients"""
    if not client_weights:
        raise ValueError("No client weights to aggregate")
    
    new_state = {}
    for key in client_weights[0].keys():
        new_state[key] = sum([w[key] for w in client_weights]) / len(client_weights)
    return new_state

def handle_client(conn, addr, client_id, round_num, global_model, client_weights, lock):
    """Handle a single client connection with performance monitoring"""
    metrics = NetworkMetrics()
    conn_start = time.time()
    
    try:
        conn.settimeout(120)  # 120 second timeout per client
        print(f"[Round {round_num}] Client {client_id}/{NUM_CLIENTS} connected from {addr}")

        # Measure connection latency (ping)
        ping_start = time.time()
        conn.send(b'PING')
        pong = conn.recv(4)
        ping_latency = (time.time() - ping_start) * 1000  # in milliseconds
        print(f"[Round {round_num}] Client {client_id} latency: {ping_latency:.2f} ms")

        # Send global model
        print(f"[Round {round_num}] Sending global model to client {client_id}...")
        send_data(conn, global_model.state_dict(), metrics)
        print(f"[Round {round_num}] Global model sent to client {client_id}")

        # Receive updated weights
        print(f"[Round {round_num}] Waiting for updates from client {client_id}...")
        recv_data = receive_data(conn, metrics)
        updated_weights = pickle.loads(recv_data)
        
        metrics.connection_time = time.time() - conn_start
        
        # Thread-safe append
        with lock:
            client_weights.append(updated_weights)
        
        print(f"[Round {round_num}] Received updates from client {client_id}")
        metrics.print_summary(client_id, round_num)
        
    except socket.timeout:
        print(f"ERROR: Client {client_id} timed out")
    except Exception as e:
        print(f"ERROR: Failed to process client {client_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def main():
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(NUM_CLIENTS * 2)  # Allow queue for all clients
        print(f"Server listening on {HOST}:{PORT}")
        print(f"Waiting for {NUM_CLIENTS} clients per round")

        global_model = SimpleNet()
        rounds = 3

        for r in range(rounds):
            print(f"\n{'='*60}")
            print(f"Round {r+1}/{rounds}")
            print(f"{'='*60}")
            
            client_weights = []
            threads = []
            lock = threading.Lock()

            # Accept all clients and handle them in parallel
            for i in range(NUM_CLIENTS):
                print(f"[Round {r+1}] Waiting for client {i+1}/{NUM_CLIENTS}...")
                conn, addr = server.accept()
                
                # Create thread for each client
                thread = threading.Thread(
                    target=handle_client,
                    args=(conn, addr, i+1, r+1, global_model, client_weights, lock)
                )
                thread.start()
                threads.append(thread)

            # Wait for all clients to finish
            print(f"[Round {r+1}] All {NUM_CLIENTS} clients connected. Processing in parallel...")
            for thread in threads:
                thread.join()

            # Aggregate updates
            if len(client_weights) == 0:
                print(f"WARNING: No client weights received in round {r+1}, skipping aggregation")
                continue
            
            try:
                new_state = aggregate_models(client_weights)
                global_model.load_state_dict(new_state)
                print(f"[Round {r+1}] Global model updated with {len(client_weights)} client updates")
            except Exception as e:
                print(f"ERROR: Failed to aggregate models: {e}")

        print("\n" + "="*50)
        print("Training complete. Saving global model...")
        torch.save(global_model.state_dict(), "global_model.pth")
        print("Global model saved to 'global_model.pth'")
        
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    except Exception as e:
        print(f"ERROR: Server error - {e}")
    finally:
        if server:
            server.close()
            print("Server socket closed")

if __name__ == "__main__":
    main()
