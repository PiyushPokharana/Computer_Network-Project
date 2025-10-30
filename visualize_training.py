"""
Visualization script for federated learning training results
Plots accuracy and loss curves from training_history.json
"""
import json
import matplotlib.pyplot as plt
import os

def plot_training_results(history_file='training_history.json'):
    """Plot accuracy and loss curves from training history"""
    
    if not os.path.exists(history_file):
        print(f"Error: {history_file} not found!")
        print("Run the server first to generate training history.")
        return
    
    # Load training history
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    rounds = history['rounds']
    accuracies = history['accuracies']
    losses = history['losses']
    num_clients = history.get('num_clients', [2] * len(rounds))
    
    if not rounds:
        print("No training data found in history file!")
        return
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot accuracy
    ax1.plot(rounds, accuracies, marker='o', linewidth=2, markersize=8, color='#2E86AB')
    ax1.set_xlabel('Training Round', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Global Model Accuracy Over Training Rounds', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim([0, 100])
    
    # Add accuracy values on points
    for i, (r, acc) in enumerate(zip(rounds, accuracies)):
        ax1.annotate(f'{acc:.1f}%', 
                    xy=(r, acc), 
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # Plot loss
    ax2.plot(rounds, losses, marker='s', linewidth=2, markersize=8, color='#A23B72')
    ax2.set_xlabel('Training Round', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax2.set_title('Global Model Loss Over Training Rounds', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Add loss values on points
    for i, (r, loss) in enumerate(zip(rounds, losses)):
        ax2.annotate(f'{loss:.3f}', 
                    xy=(r, loss), 
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    
    # Save plot
    output_file = 'training_results.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Plot saved to '{output_file}'")
    
    # Print summary
    print(f"\n{'='*50}")
    print("Training Summary")
    print(f"{'='*50}")
    print(f"Total Rounds: {len(rounds)}")
    print(f"Initial Accuracy: {accuracies[0]:.2f}%")
    print(f"Final Accuracy: {accuracies[-1]:.2f}%")
    print(f"Best Accuracy: {max(accuracies):.2f}%")
    print(f"Improvement: {accuracies[-1] - accuracies[0]:.2f}%")
    print(f"Average Clients/Round: {sum(num_clients)/len(num_clients):.1f}")
    print(f"{'='*50}")
    
    # Show plot
    try:
        plt.show()
    except:
        print("Note: Could not display plot window. Plot saved to file.")

def main():
    print("Federated Learning Training Visualization")
    print("=" * 50)
    plot_training_results()

if __name__ == "__main__":
    main()
