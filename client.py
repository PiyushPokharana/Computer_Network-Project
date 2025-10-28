import socket
import pickle
import torch
from model_def import SimpleNet

SERVER_IP = "192.168.107.136"   # Replace with actual server IP
PORT = 5000

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

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, PORT))
    print("Connected to server.")

    # Receive global model
    recv_data = b""
    while True:
        packet = client.recv(4096)
        if not packet:
            break
        recv_data += packet
    global_state = pickle.loads(recv_data)
    model = SimpleNet()
    model.load_state_dict(global_state)

    # Perform local training
    updated_state = local_train(model)

    # Send updated weights
    data = pickle.dumps(updated_state)
    client.sendall(data)
    client.close()
    print("Sent updated model back to server.")

if __name__ == "__main__":
    main()
