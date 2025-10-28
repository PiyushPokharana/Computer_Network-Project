import socket
import pickle
import torch
from model_def import SimpleNet

HOST = '0.0.0.0'   # Listen on all network interfaces
PORT = 5000
NUM_CLIENTS = 2

def aggregate_models(client_weights):
    """Average model weights from all clients"""
    new_state = {}
    for key in client_weights[0].keys():
        new_state[key] = sum([w[key] for w in client_weights]) / len(client_weights)
    return new_state

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(NUM_CLIENTS)
    print(f"Server listening on {HOST}:{PORT}")

    global_model = SimpleNet()
    rounds = 3

    for r in range(rounds):
        print(f"\n--- Round {r+1} ---")
        client_weights = []

        for i in range(NUM_CLIENTS):
            conn, addr = server.accept()
            print(f"Connected to Client {i+1} at {addr}")

            # Send global model
            data = pickle.dumps(global_model.state_dict())
            conn.sendall(data)

            # Receive updated weights
            recv_data = b""
            while True:
                packet = conn.recv(4096)
                if not packet:
                    break
                recv_data += packet
            updated_weights = pickle.loads(recv_data)
            client_weights.append(updated_weights)
            conn.close()

        # Aggregate updates
        new_state = aggregate_models(client_weights)
        global_model.load_state_dict(new_state)
        print("Server updated global model.")

    print("Training complete. Saving global model...")
    torch.save(global_model.state_dict(), "global_model.pth")

if __name__ == "__main__":
    main()
