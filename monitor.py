"""
Real-time Training Monitor for Federated Learning

Monitors training progress by reading the training_history.json file
and displaying live updates in the terminal.

Usage:
    python monitor.py [refresh_interval]
    
Example:
    python monitor.py 2    # Refresh every 2 seconds (default)
    python monitor.py 5    # Refresh every 5 seconds
"""

import json
import time
import os
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_training(history_file='training_history.json', interval=2):
    """Monitor training progress in real-time"""
    print("Starting training monitor... (Press Ctrl+C to stop)")
    print("Waiting for training to start...\n")
    
    last_rounds = 0
    
    try:
        while True:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                current_rounds = len(history['rounds'])
                
                if current_rounds > last_rounds:
                    clear_screen()
                    print("="*70)
                    print("🔄 FEDERATED LEARNING TRAINING MONITOR")
                    print("="*70)
                    print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Monitoring: {history_file}")
                    print("="*70)
                    
                    if current_rounds > 0:
                        print(f"\n📊 Current Progress:")
                        print(f"  Round: {history['rounds'][-1]}")
                        print(f"  Accuracy: {history['accuracies'][-1]:.2f}%")
                        print(f"  Loss: {history['losses'][-1]:.4f}")
                        print(f"  Clients: {history['num_clients'][-1]}")
                        
                        if current_rounds > 1:
                            acc_change = history['accuracies'][-1] - history['accuracies'][-2]
                            loss_change = history['losses'][-1] - history['losses'][-2]
                            
                            print(f"\n📈 Change from Last Round:")
                            print(f"  Accuracy: {acc_change:+.2f}%")
                            print(f"  Loss: {loss_change:+.4f}")
                        
                        print(f"\n🏆 Best So Far:")
                        print(f"  Accuracy: {max(history['accuracies']):.2f}%")
                        print(f"  Loss: {min(history['losses']):.4f}")
                        
                        print(f"\n📝 Training History:")
                        print(f"{'Round':<10}{'Accuracy':<15}{'Loss':<15}{'Clients':<10}")
                        print("-"*50)
                        for i in range(len(history['rounds'])):
                            print(f"{history['rounds'][i]:<10}{history['accuracies'][i]:<15.2f}"
                                  f"{history['losses'][i]:<15.4f}{history['num_clients'][i]:<10}")
                    
                    last_rounds = current_rounds
                    print("\n" + "="*70)
                    print(f"Refreshing every {interval} seconds... (Ctrl+C to stop)")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print("\nRun 'python visualize_training.py' to generate charts!")

if __name__ == "__main__":
    import sys
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    monitor_training(interval=interval)
