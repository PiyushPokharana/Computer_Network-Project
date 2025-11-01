"""
Data utilities for federated learning
Provides non-IID data distribution and other data partitioning strategies
"""
import torch
import numpy as np
from torch.utils.data import Subset
from torchvision import datasets, transforms


def create_iid_split(dataset, num_clients):
    """
    Create IID (Independent and Identically Distributed) data splits
    Each client gets random samples from the dataset
    
    Args:
        dataset: PyTorch dataset
        num_clients: Number of clients to split data for
        
    Returns:
        dict: {client_id: list of indices}
    """
    num_items = len(dataset)
    items_per_client = num_items // num_clients
    client_data = {}
    all_idxs = list(range(num_items))
    
    for i in range(num_clients):
        client_data[i] = set(np.random.choice(all_idxs, items_per_client, replace=False))
        all_idxs = list(set(all_idxs) - client_data[i])
        client_data[i] = list(client_data[i])
    
    return client_data


def create_non_iid_split(dataset, num_clients, num_shards_per_client=2):
    """
    Create non-IID data splits where each client gets data from limited classes
    This simulates real-world scenarios where clients have biased data
    
    Args:
        dataset: PyTorch dataset with labels
        num_clients: Number of clients
        num_shards_per_client: Number of shards (data groups) each client gets
        
    Returns:
        dict: {client_id: list of indices}
    """
    num_items = len(dataset)
    num_shards = num_clients * num_shards_per_client
    shard_size = num_items // num_shards
    
    # Get all labels
    if hasattr(dataset, 'targets'):
        labels = np.array(dataset.targets)
    elif hasattr(dataset, 'labels'):
        labels = np.array(dataset.labels)
    else:
        # Extract labels manually
        labels = np.array([dataset[i][1] for i in range(len(dataset))])
    
    # Sort indices by label
    idxs = np.arange(num_items)
    idxs_labels = np.vstack((idxs, labels))
    idxs_labels = idxs_labels[:, idxs_labels[1, :].argsort()]
    idxs = idxs_labels[0, :].astype(int)
    
    # Divide into shards
    shard_idxs = [idxs[i:i + shard_size] for i in range(0, len(idxs), shard_size)]
    
    # Randomly assign shards to clients
    np.random.shuffle(shard_idxs)
    client_data = {i: [] for i in range(num_clients)}
    
    for i in range(num_clients):
        for j in range(num_shards_per_client):
            shard_idx = i * num_shards_per_client + j
            if shard_idx < len(shard_idxs):
                client_data[i].extend(shard_idxs[shard_idx])
    
    return client_data


def create_class_based_split(dataset, num_clients, classes_per_client=2):
    """
    Create non-IID splits where each client gets data from specific classes only
    
    Args:
        dataset: PyTorch dataset
        num_clients: Number of clients
        classes_per_client: Number of classes each client has access to
        
    Returns:
        dict: {client_id: list of indices}
    """
    # Get labels
    if hasattr(dataset, 'targets'):
        labels = np.array(dataset.targets)
    elif hasattr(dataset, 'labels'):
        labels = np.array(dataset.labels)
    else:
        labels = np.array([dataset[i][1] for i in range(len(dataset))])
    
    num_classes = len(np.unique(labels))
    client_data = {i: [] for i in range(num_clients)}
    
    # Group indices by class
    class_idxs = {c: np.where(labels == c)[0] for c in range(num_classes)}
    
    # Assign classes to clients
    for client_id in range(num_clients):
        # Select specific classes for this client
        client_classes = np.random.choice(num_classes, classes_per_client, replace=False)
        
        for cls in client_classes:
            # Give this client a portion of data from this class
            cls_samples = class_idxs[cls]
            samples_per_client = len(cls_samples) // (num_clients // classes_per_client + 1)
            start_idx = (client_id % (num_clients // classes_per_client)) * samples_per_client
            end_idx = start_idx + samples_per_client
            
            client_data[client_id].extend(cls_samples[start_idx:end_idx])
    
    return client_data


def get_client_dataloader(dataset, client_indices, batch_size=32, shuffle=True):
    """
    Create a DataLoader for a specific client's data subset
    
    Args:
        dataset: PyTorch dataset
        client_indices: List of indices for this client
        batch_size: Batch size for training
        shuffle: Whether to shuffle the data
        
    Returns:
        DataLoader for the client's data
    """
    from torch.utils.data import DataLoader
    
    client_dataset = Subset(dataset, client_indices)
    return DataLoader(client_dataset, batch_size=batch_size, shuffle=shuffle)


def analyze_data_distribution(dataset, client_data):
    """
    Analyze and print statistics about data distribution across clients
    
    Args:
        dataset: PyTorch dataset
        client_data: dict mapping client_id to indices
    """
    # Get labels
    if hasattr(dataset, 'targets'):
        labels = np.array(dataset.targets)
    elif hasattr(dataset, 'labels'):
        labels = np.array(dataset.labels)
    else:
        labels = np.array([dataset[i][1] for i in range(len(dataset))])
    
    num_classes = len(np.unique(labels))
    
    print(f"\n{'='*60}")
    print("Data Distribution Analysis")
    print(f"{'='*60}")
    
    for client_id, indices in client_data.items():
        client_labels = labels[indices]
        unique, counts = np.unique(client_labels, return_counts=True)
        
        print(f"\nClient {client_id}:")
        print(f"  Total samples: {len(indices)}")
        print(f"  Classes present: {len(unique)}/{num_classes}")
        print(f"  Class distribution:")
        
        for cls, count in zip(unique, counts):
            percentage = 100 * count / len(indices)
            print(f"    Class {cls}: {count:5d} samples ({percentage:5.1f}%)")
    
    print(f"\n{'='*60}\n")


# Example usage
if __name__ == "__main__":
    # Load MNIST for demonstration
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    
    num_clients = 3
    
    print("Testing IID split...")
    iid_data = create_iid_split(dataset, num_clients)
    analyze_data_distribution(dataset, iid_data)
    
    print("\nTesting non-IID split...")
    non_iid_data = create_non_iid_split(dataset, num_clients, num_shards_per_client=2)
    analyze_data_distribution(dataset, non_iid_data)
    
    print("\nTesting class-based split (2 classes per client)...")
    class_based_data = create_class_based_split(dataset, num_clients, classes_per_client=2)
    analyze_data_distribution(dataset, class_based_data)
