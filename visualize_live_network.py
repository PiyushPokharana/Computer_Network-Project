"""
Real-Time Federated Learning Network Visualization
Shows live animation of:
- Network topology (server + clients)
- Packet transmission (animated)
- Training progress at each node
- Model aggregation
"""

import json
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from pathlib import Path
from datetime import datetime

class LiveNetworkVisualizer:
    """Real-time visualization of federated learning network"""
    
    def __init__(self, num_clients=2):
        self.num_clients = num_clients
        self.training_file = Path("training_history.json")
        self.metrics_file = Path("performance_metrics.json")
        
        # Animation state
        self.current_round = 0
        self.phase = "idle"  # idle, distributing, training, collecting, aggregating
        self.packet_positions = []
        self.training_progress = {i: 0 for i in range(num_clients)}
        
        # Load data
        self.training_data = None
        self.metrics_data = None
        self.last_load_time = 0
        
        # Setup figure
        self.setup_figure()
        
    def setup_figure(self):
        """Initialize the figure and layout"""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('🌐 Federated Learning Network - Live Visualization', 
                         fontsize=16, fontweight='bold')
        
        # Main network view
        self.ax_network = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=2)
        self.ax_network.set_xlim(-1, 11)
        self.ax_network.set_ylim(-1, 11)
        self.ax_network.axis('off')
        self.ax_network.set_aspect('equal')
        
        # Training metrics
        self.ax_accuracy = plt.subplot2grid((3, 3), (0, 2))
        self.ax_loss = plt.subplot2grid((3, 3), (1, 2))
        
        # Status panel
        self.ax_status = plt.subplot2grid((3, 3), (2, 0), colspan=3)
        self.ax_status.axis('off')
        
        # Network positions
        self.server_pos = (5, 8)
        self.client_positions = self._calculate_client_positions()
        
    def _calculate_client_positions(self):
        """Calculate positions for clients in a circle below server"""
        positions = []
        radius = 3
        center_y = 3
        
        if self.num_clients == 1:
            positions.append((5, center_y))
        else:
            for i in range(self.num_clients):
                angle = np.pi + (i * np.pi / (self.num_clients - 1))
                x = 5 + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)
                positions.append((x, y))
        
        return positions
    
    def load_data(self):
        """Load training data and metrics"""
        current_time = time.time()
        
        # Only reload every 0.5 seconds
        if current_time - self.last_load_time < 0.5:
            return
        
        self.last_load_time = current_time
        
        if self.training_file.exists():
            with open(self.training_file, 'r') as f:
                self.training_data = json.load(f)
        
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                self.metrics_data = json.load(f)
    
    def draw_network_topology(self):
        """Draw server and clients"""
        self.ax_network.clear()
        self.ax_network.set_xlim(-1, 11)
        self.ax_network.set_ylim(-1, 11)
        self.ax_network.axis('off')
        
        # Draw connections (dashed lines)
        for client_pos in self.client_positions:
            self.ax_network.plot([self.server_pos[0], client_pos[0]], 
                                [self.server_pos[1], client_pos[1]], 
                                'k--', alpha=0.3, linewidth=1)
        
        # Draw server
        server_circle = plt.Circle(self.server_pos, 0.8, color='#FF6B6B', 
                                  ec='black', linewidth=3, zorder=10)
        self.ax_network.add_patch(server_circle)
        self.ax_network.text(self.server_pos[0], self.server_pos[1], 
                           'SERVER', 
                           ha='center', va='center', fontsize=12, 
                           fontweight='bold', zorder=11)
        
        # Draw clients
        for i, pos in enumerate(self.client_positions):
            # Client color based on training progress
            progress = self.training_progress.get(i, 0)
            if progress > 0:
                color = plt.cm.Greens(0.3 + progress * 0.6)
            else:
                color = '#4ECDC4'
            
            client_circle = plt.Circle(pos, 0.6, color=color, 
                                      ec='black', linewidth=2, zorder=10)
            self.ax_network.add_patch(client_circle)
            self.ax_network.text(pos[0], pos[1], 
                               f'CLIENT\n{i}', 
                               ha='center', va='center', fontsize=10,
                               fontweight='bold', zorder=11)
            
            # Show training progress
            if progress > 0:
                self.ax_network.text(pos[0], pos[1] - 1.2, 
                                   f'{int(progress*100)}%', 
                                   ha='center', va='top', fontsize=9,
                                   color='green', fontweight='bold')
    
    def draw_packets(self, frame):
        """Draw animated packets"""
        # Update packet positions based on phase
        if self.phase == "distributing":
            # Packets from server to clients
            for i, client_pos in enumerate(self.client_positions):
                progress = (frame % 30) / 30  # Animation cycle
                x = self.server_pos[0] + progress * (client_pos[0] - self.server_pos[0])
                y = self.server_pos[1] + progress * (client_pos[1] - self.server_pos[1])
                
                # Draw packet
                packet = plt.Circle((x, y), 0.2, color='blue', 
                                  alpha=0.7, zorder=15)
                self.ax_network.add_patch(packet)
                self.ax_network.text(x, y, 'M', ha='center', va='center', 
                                   fontsize=10, fontweight='bold', zorder=16)
        
        elif self.phase == "collecting":
            # Packets from clients to server
            for i, client_pos in enumerate(self.client_positions):
                progress = (frame % 30) / 30
                x = client_pos[0] + progress * (self.server_pos[0] - client_pos[0])
                y = client_pos[1] + progress * (self.server_pos[1] - client_pos[1])
                
                packet = plt.Circle((x, y), 0.2, color='green', 
                                  alpha=0.7, zorder=15)
                self.ax_network.add_patch(packet)
                self.ax_network.text(x, y, 'U', ha='center', va='center', 
                                   fontsize=10, fontweight='bold', zorder=16)
    
    def draw_phase_indicator(self):
        """Draw current phase indicator"""
        phase_text = {
            "idle": "[IDLE] Waiting to start",
            "distributing": "[SEND] Distributing global model to clients",
            "training": "[TRAIN] Clients training on local data",
            "collecting": "[RECV] Collecting trained models from clients",
            "aggregating": "[AGG] Server aggregating models (FedAvg)"
        }
        
        title = phase_text.get(self.phase, "")
        if self.current_round > 0:
            title = f"Round {self.current_round}/5 - {title}"
        
        self.ax_network.text(5, 10.5, title, 
                           ha='center', va='top', fontsize=11,
                           fontweight='bold',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def update_metrics_plots(self):
        """Update accuracy and loss plots"""
        if not self.training_data:
            return
        
        rounds = self.training_data.get('rounds', [])
        accuracies = self.training_data.get('accuracies', [])
        losses = self.training_data.get('losses', [])
        
        if not rounds or not accuracies:
            return
        
        # Accuracy plot
        self.ax_accuracy.clear()
        self.ax_accuracy.plot(rounds, accuracies, 'o-', 
                             color='green', linewidth=2, markersize=8)
        self.ax_accuracy.set_title('Test Accuracy', fontweight='bold')
        self.ax_accuracy.set_ylabel('Accuracy (%)')
        self.ax_accuracy.grid(True, alpha=0.3)
        if accuracies:
            self.ax_accuracy.set_ylim(min(accuracies)-2, max(accuracies)+2)
        
        # Loss plot
        self.ax_loss.clear()
        self.ax_loss.plot(rounds, losses, 'o-', 
                         color='red', linewidth=2, markersize=8)
        self.ax_loss.set_title('Test Loss', fontweight='bold')
        self.ax_loss.set_xlabel('Round')
        self.ax_loss.set_ylabel('Loss')
        self.ax_loss.grid(True, alpha=0.3)
    
    def update_status_panel(self):
        """Update status information panel"""
        self.ax_status.clear()
        self.ax_status.axis('off')
        
        status_text = "System Status\n"
        status_text += "=" * 80 + "\n"
        
        if self.training_data:
            rounds = self.training_data.get('rounds', [])
            accuracies = self.training_data.get('accuracies', [])
            losses = self.training_data.get('losses', [])
            
            if rounds and accuracies:
                status_text += f"Completed Rounds: {len(rounds)}\n"
                status_text += f"Current Accuracy: {accuracies[-1]:.2f}%\n"
                status_text += f"Current Loss: {losses[-1]:.4f}\n"
        
        if self.metrics_data:
            bytes_sent = self.metrics_data.get('bytes_sent', [])
            bytes_received = self.metrics_data.get('bytes_received', [])
            if bytes_sent and bytes_received:
                total_data = sum(bytes_sent) + sum(bytes_received)
                status_text += f"Total Network Traffic: {total_data/1024/1024:.2f} MB\n"
        
        status_text += f"Current Phase: {self.phase.upper()}\n"
        status_text += f"Active Clients: {self.num_clients}\n"
        
        self.ax_status.text(0.05, 0.5, status_text, 
                          transform=self.ax_status.transAxes,
                          fontsize=10, verticalalignment='center',
                          family='monospace',
                          bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    def simulate_phase_progression(self, frame):
        """Simulate phase transitions for demo"""
        # Load real data
        self.load_data()
        
        # Determine current state from data
        if self.training_data:
            rounds = self.training_data.get('rounds', [])
            self.current_round = len(rounds)
        
        # Simulate phases
        cycle = frame % 150  # Full cycle: 150 frames
        
        if cycle < 20:
            self.phase = "distributing"
            for i in range(self.num_clients):
                self.training_progress[i] = 0
        elif cycle < 80:
            self.phase = "training"
            progress = (cycle - 20) / 60
            for i in range(self.num_clients):
                self.training_progress[i] = min(1.0, progress + np.random.random()*0.1)
        elif cycle < 100:
            self.phase = "collecting"
            for i in range(self.num_clients):
                self.training_progress[i] = 1.0
        elif cycle < 120:
            self.phase = "aggregating"
        else:
            self.phase = "idle"
    
    def animate(self, frame):
        """Animation function called for each frame"""
        # Update phase
        self.simulate_phase_progression(frame)
        
        # Draw everything
        self.draw_network_topology()
        self.draw_packets(frame)
        self.draw_phase_indicator()
        self.update_metrics_plots()
        self.update_status_panel()
    
    def show(self, interval=50):
        """Start the animation"""
        anim = FuncAnimation(self.fig, self.animate, frames=None,
                           interval=interval, blit=False, repeat=True)
        plt.tight_layout()
        plt.show()
        return anim


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🌐 REAL-TIME FEDERATED LEARNING NETWORK VISUALIZATION")
    print("="*60)
    
    print("\n📡 Starting live network monitor...")
    print("   - Animated packet transmission")
    print("   - Real-time training progress")
    print("   - Live metrics updates")
    
    print("\n💡 TIP: Run training in another terminal to see live updates!")
    print("   Terminal 1: python server.py")
    print("   Terminal 2: python client.py (CLIENT_ID=0)")
    print("   Terminal 3: python client.py (CLIENT_ID=1)")
    
    print("\n🎨 Starting visualization...")
    print("   (Close window to exit)")
    print("="*60 + "\n")
    
    try:
        visualizer = LiveNetworkVisualizer(num_clients=2)
        visualizer.show(interval=50)
    except KeyboardInterrupt:
        print("\n\n⏹️  Visualization stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
