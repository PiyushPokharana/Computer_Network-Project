import socket
import pickle
import torch
import os
from model_def import SimpleNet

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "5000"))
NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))

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

def main():
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(NUM_CLIENTS)
        print(f"Server listening on {HOST}:{PORT}")
        print(f"Waiting for {NUM_CLIENTS} clients per round")

        global_model = SimpleNet()
        rounds = 3

        for r in range(rounds):
            print(f"\n{'='*50}")
            print(f"Round {r+1}/{rounds}")
            print(f"{'='*50}")
            client_weights = []

            for i in range(NUM_CLIENTS):
                conn = None
                try:
                    conn, addr = server.accept()
                    conn.settimeout(60)  # 60 second timeout per client
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