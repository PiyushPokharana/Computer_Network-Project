import socket
import pickle
import torch
import os
from model_def import SimpleNet

HOST = os.environ.get("HOST", "0.0.0.0")  # Listen on all network interfaces
PORT = int(os.environ.get("PORT", "5000"))
NUM_CLIENTS = int(os.environ.get("NUM_CLIENTS", "2"))
NUM_ROUNDS = int(os.environ.get("NUM_ROUNDS", "3"))

def aggregate_models(client_weights):
    """Average model weights from all clients (FedAvg)"""
    new_state = {}
    for key in client_weights[0].keys():
        new_state[key] = sum([w[key] for w in client_weights]) / len(client_weights)
    return new_state

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
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(NUM_CLIENTS)
        print(f"🚀 Server listening on {HOST}:{PORT}")
        print(f"📊 Waiting for {NUM_CLIENTS} clients")
        print(f"🔄 Training rounds: {NUM_ROUNDS}\n")

        global_model = SimpleNet()

        for r in range(NUM_ROUNDS):
            print(f"\n{'='*50}")
            print(f"📍 Round {r+1}/{NUM_ROUNDS}")
            print(f"{'='*50}")
            client_weights = []

            for i in range(NUM_CLIENTS):
                try:
                    conn, addr = server.accept()
                    conn.settimeout(60)  # 60 second timeout per client
                    print(f"✅ Client {i+1} connected from {addr}")

                    # Send global model
                    print(f"   📤 Sending global model to Client {i+1}...")
                    send_data(conn, global_model.state_dict())
                    print(f"   ✓ Model sent to Client {i+1}")

                    # Receive updated weights
                    print(f"   📥 Waiting for updates from Client {i+1}...")
                    recv_data = receive_data(conn)
                    updated_weights = pickle.loads(recv_data)
                    client_weights.append(updated_weights)
                    print(f"   ✓ Received updates from Client {i+1}")
                    
                    conn.close()
                except socket.timeout:
                    print(f"   ⚠️  Client {i+1} timed out")
                except Exception as e:
                    print(f"   ❌ Error with Client {i+1}: {e}")

            if not client_weights:
                print("\n❌ No client updates received. Stopping training.")
                break

            # Aggregate updates
            print(f"\n🔄 Aggregating {len(client_weights)} client updates...")
            new_state = aggregate_models(client_weights)
            global_model.load_state_dict(new_state)
            print(f"✅ Global model updated successfully")

        print(f"\n{'='*50}")
        print("🎉 Training complete!")
        print(f"{'='*50}")
        print("💾 Saving global model to 'global_model.pth'...")
        torch.save(global_model.state_dict(), "global_model.pth")
        print("✅ Model saved successfully")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Server interrupted by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        if server:
            server.close()
            print("\n🔌 Server shut down")

if __name__ == "__main__":
    main()
