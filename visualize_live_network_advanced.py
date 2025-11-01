"""
Advanced Real-Time Network Visualization with Recording
Features:
- Live packet animation with trails
- Network latency simulation
- Bandwidth visualization
- Save animation to MP4/GIF
- Enhanced visual effects
"""

import json
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import deque

class AdvancedNetworkVisualizer:
    """Advanced real-time visualization with effects"""
    
    def __init__(self, num_clients=2, save_video=False):
        self.num_clients = num_clients
        self.save_video = save_video
        self.training_file = Path("training_history.json")
        self.metrics_file = Path("performance_metrics.json")
        
        # Animation state
        self.current_round = 0
        self.phase = "idle"
        self.packets = []  # List of active packets
        self.packet_trails = []  # Packet movement trails
        self.training_progress = {i: 0 for i in range(num_clients)}
        self.bandwidth_usage = deque(maxlen=50)
        self.latency_display = {i: 0 for i in range(num_clients)}
        
        # Load data
        self.training_data = None
        self.metrics_data = None
        self.last_load_time = 0
        
        # Setup figure with dark theme
        plt.style.use('dark_background')
        self.setup_figure()
        
    def setup_figure(self):
        """Initialize the figure with enhanced layout"""
        self.fig = plt.figure(figsize=(18, 11), facecolor='#1a1a1a')
        self.fig.suptitle('🌐 Federated Learning Network - Live Monitor', 
                         fontsize=18, fontweight='bold', color='#00FF00')
        
        # Main network view (larger)
        self.ax_network = plt.subplot2grid((4, 4), (0, 0), colspan=3, rowspan=3)
        self.ax_network.set_xlim(-1, 11)
        self.ax_network.set_ylim(-1, 11)
        self.ax_network.axis('off')
        self.ax_network.set_aspect('equal')
        self.ax_network.set_facecolor('#0a0a0a')
        
        # Metrics
        self.ax_accuracy = plt.subplot2grid((4, 4), (0, 3))
        self.ax_loss = plt.subplot2grid((4, 4), (1, 3))
        self.ax_bandwidth = plt.subplot2grid((4, 4), (2, 3))
        
        # Status panel
        self.ax_status = plt.subplot2grid((4, 4), (3, 0), colspan=4)
        self.ax_status.axis('off')
        self.ax_status.set_facecolor('#1a1a1a')
        
        # Network positions
        self.server_pos = (5, 8)
        self.client_positions = self._calculate_client_positions()
        
    def _calculate_client_positions(self):
        """Calculate positions for clients"""
        positions = []
        radius = 3.5
        center_y = 2.5
        
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
        
        if current_time - self.last_load_time < 0.3:
            return
        
        self.last_load_time = current_time
        
        if self.training_file.exists():
            try:
                with open(self.training_file, 'r') as f:
                    self.training_data = json.load(f)
            except:
                pass
        
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    self.metrics_data = json.load(f)
            except:
                pass
    
    def create_packet(self, start_pos, end_pos, packet_type):
        """Create a new packet"""
        return {
            'start': start_pos,
            'end': end_pos,
            'progress': 0,
            'type': packet_type,  # 'model', 'update', 'data'
            'trail': deque(maxlen=10)
        }
    
    def update_packets(self, frame):
        """Update packet positions"""
        # Add new packets based on phase
        if frame % 5 == 0:  # Add packets periodically
            if self.phase == "distributing":
                for client_pos in self.client_positions:
                    self.packets.append(
                        self.create_packet(self.server_pos, client_pos, 'model')
                    )
            elif self.phase == "collecting":
                for client_pos in self.client_positions:
                    self.packets.append(
                        self.create_packet(client_pos, self.server_pos, 'update')
                    )
        
        # Update existing packets
        packets_to_remove = []
        for packet in self.packets:
            packet['progress'] += 0.05
            
            # Calculate current position
            t = packet['progress']
            x = packet['start'][0] + t * (packet['end'][0] - packet['start'][0])
            y = packet['start'][1] + t * (packet['end'][1] - packet['start'][1])
            
            # Add to trail
            packet['trail'].append((x, y))
            
            # Remove if reached destination
            if t >= 1.0:
                packets_to_remove.append(packet)
        
        # Remove completed packets
        for packet in packets_to_remove:
            self.packets.remove(packet)
    
    def draw_network_topology(self):
        """Draw network with enhanced visuals"""
        self.ax_network.clear()
        self.ax_network.set_xlim(-1, 11)
        self.ax_network.set_ylim(-1, 11)
        self.ax_network.axis('off')
        self.ax_network.set_facecolor('#0a0a0a')
        
        # Draw connections with glow effect
        for i, client_pos in enumerate(self.client_positions):
            # Glow effect
            for width, alpha in [(4, 0.1), (3, 0.15), (2, 0.2)]:
                self.ax_network.plot([self.server_pos[0], client_pos[0]], 
                                    [self.server_pos[1], client_pos[1]], 
                                    color='cyan', alpha=alpha, linewidth=width, zorder=1)
            
            # Main line
            self.ax_network.plot([self.server_pos[0], client_pos[0]], 
                                [self.server_pos[1], client_pos[1]], 
                                'cyan', alpha=0.5, linewidth=1, linestyle='--', zorder=2)
            
            # Show latency
            mid_x = (self.server_pos[0] + client_pos[0]) / 2
            mid_y = (self.server_pos[1] + client_pos[1]) / 2
            latency = self.latency_display.get(i, 0)
            if latency > 0:
                self.ax_network.text(mid_x, mid_y, f'{latency}ms', 
                                   ha='center', fontsize=8, color='yellow',
                                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        # Draw server with glow
        for radius, alpha in [(1.2, 0.1), (1.0, 0.2), (0.8, 0.3)]:
            glow = plt.Circle(self.server_pos, radius, color='red', 
                            alpha=alpha, zorder=8)
            self.ax_network.add_patch(glow)
        
        server_circle = plt.Circle(self.server_pos, 0.7, color='#FF3333', 
                                  ec='#FF6666', linewidth=3, zorder=10)
        self.ax_network.add_patch(server_circle)
        self.ax_network.text(self.server_pos[0], self.server_pos[1], 
                           '🖥️', ha='center', va='center', 
                           fontsize=30, zorder=11)
        self.ax_network.text(self.server_pos[0], self.server_pos[1] - 1.2, 
                           'Server', ha='center', fontsize=10, 
                           fontweight='bold', color='white')
        
        # Draw clients
        for i, pos in enumerate(self.client_positions):
            progress = self.training_progress.get(i, 0)
            
            # Color based on progress
            if progress > 0:
                color = (0, 1 - progress * 0.5, progress)  # Green gradient
            else:
                color = '#3399FF'
            
            # Glow effect
            for radius, alpha in [(0.9, 0.1), (0.7, 0.2)]:
                glow = plt.Circle(pos, radius, color=color, 
                                alpha=alpha, zorder=8)
                self.ax_network.add_patch(glow)
            
            client_circle = plt.Circle(pos, 0.6, color=color, 
                                      ec='#66CCFF', linewidth=2, zorder=10)
            self.ax_network.add_patch(client_circle)
            self.ax_network.text(pos[0], pos[1], '💻', 
                               ha='center', va='center', 
                               fontsize=24, zorder=11)
            self.ax_network.text(pos[0], pos[1] - 1.0, 
                               f'Client {i}', ha='center', fontsize=9,
                               fontweight='bold', color='white')
            
            # Progress bar
            if progress > 0:
                bar_y = pos[1] + 0.9
                bar_width = 1.0
                bar_height = 0.15
                
                # Background
                bg_rect = patches.Rectangle((pos[0] - bar_width/2, bar_y), 
                                           bar_width, bar_height,
                                           facecolor='gray', alpha=0.3, zorder=12)
                self.ax_network.add_patch(bg_rect)
                
                # Progress
                prog_rect = patches.Rectangle((pos[0] - bar_width/2, bar_y), 
                                             bar_width * progress, bar_height,
                                             facecolor='lime', alpha=0.8, zorder=13)
                self.ax_network.add_patch(prog_rect)
                
                # Text
                self.ax_network.text(pos[0], bar_y + 0.35, 
                                   f'{int(progress*100)}%', 
                                   ha='center', fontsize=8,
                                   color='lime', fontweight='bold')
    
    def draw_packets(self):
        """Draw animated packets with trails"""
        for packet in self.packets:
            # Draw trail
            if len(packet['trail']) > 1:
                trail_x = [p[0] for p in packet['trail']]
                trail_y = [p[1] for p in packet['trail']]
                self.ax_network.plot(trail_x, trail_y, 
                                   color='yellow', alpha=0.3, 
                                   linewidth=2, zorder=14)
            
            # Current position
            if packet['trail']:
                x, y = packet['trail'][-1]
                
                # Packet appearance based on type
                if packet['type'] == 'model':
                    color, emoji = 'blue', '📦'
                elif packet['type'] == 'update':
                    color, emoji = 'green', '📊'
                else:
                    color, emoji = 'yellow', '📡'
                
                # Glow
                glow = plt.Circle((x, y), 0.3, color=color, 
                                alpha=0.5, zorder=15)
                self.ax_network.add_patch(glow)
                
                # Packet
                packet_circle = plt.Circle((x, y), 0.2, color=color, 
                                         alpha=0.8, ec='white', linewidth=1, zorder=16)
                self.ax_network.add_patch(packet_circle)
                self.ax_network.text(x, y, emoji, 
                                   ha='center', va='center', 
                                   fontsize=8, zorder=17)
    
    def draw_phase_indicator(self):
        """Draw enhanced phase indicator"""
        phase_info = {
            "idle": ("⏸️ IDLE", "Waiting to start", '#888888'),
            "distributing": ("📤 DISTRIBUTING", "Sending model to clients", '#3399FF'),
            "training": ("🔄 TRAINING", "Clients training locally", '#FF9933'),
            "collecting": ("📥 COLLECTING", "Gathering updates", '#33FF33'),
            "aggregating": ("⚡ AGGREGATING", "FedAvg aggregation", '#FF33FF')
        }
        
        emoji, text, color = phase_info.get(self.phase, ("", "", "white"))
        title = f"{emoji} {text}"
        
        if self.current_round > 0:
            title = f"Round {self.current_round}/5 │ {title}"
        
        # Draw fancy box
        self.ax_network.text(5, 10.3, title, 
                           ha='center', va='top', fontsize=12,
                           fontweight='bold', color=color,
                           bbox=dict(boxstyle='round,pad=0.5', 
                                   facecolor='black', 
                                   edgecolor=color,
                                   linewidth=2,
                                   alpha=0.8))
    
    def update_metrics_plots(self):
        """Update metric plots with styling"""
        if not self.training_data:
            return
        
        rounds = self.training_data.get('rounds', [])
        if not rounds:
            return
        
        round_nums = [r['round'] for r in rounds]
        accuracies = [r['test_accuracy'] * 100 for r in rounds]
        losses = [r['test_loss'] for r in rounds]
        
        # Accuracy plot
        self.ax_accuracy.clear()
        self.ax_accuracy.plot(round_nums, accuracies, 'o-', 
                             color='#00FF00', linewidth=2, markersize=6)
        self.ax_accuracy.fill_between(round_nums, accuracies, alpha=0.3, color='green')
        self.ax_accuracy.set_title('📈 Test Accuracy', fontweight='bold', color='white')
        self.ax_accuracy.set_ylabel('Accuracy (%)', color='white')
        self.ax_accuracy.grid(True, alpha=0.2, color='gray')
        self.ax_accuracy.set_facecolor('#1a1a1a')
        
        # Loss plot
        self.ax_loss.clear()
        self.ax_loss.plot(round_nums, losses, 'o-', 
                         color='#FF3333', linewidth=2, markersize=6)
        self.ax_loss.fill_between(round_nums, losses, alpha=0.3, color='red')
        self.ax_loss.set_title('📉 Test Loss', fontweight='bold', color='white')
        self.ax_loss.set_ylabel('Loss', color='white')
        self.ax_loss.grid(True, alpha=0.2, color='gray')
        self.ax_loss.set_facecolor('#1a1a1a')
        
        # Bandwidth plot
        self.ax_bandwidth.clear()
        if len(self.bandwidth_usage) > 0:
            self.ax_bandwidth.plot(list(self.bandwidth_usage), 
                                  color='#FFAA00', linewidth=2)
            self.ax_bandwidth.fill_between(range(len(self.bandwidth_usage)), 
                                          list(self.bandwidth_usage), 
                                          alpha=0.3, color='orange')
        self.ax_bandwidth.set_title('📡 Network Activity', fontweight='bold', color='white')
        self.ax_bandwidth.set_ylabel('Packets/s', color='white')
        self.ax_bandwidth.set_ylim(0, 20)
        self.ax_bandwidth.grid(True, alpha=0.2, color='gray')
        self.ax_bandwidth.set_facecolor('#1a1a1a')
    
    def update_status_panel(self):
        """Update status panel with rich formatting"""
        self.ax_status.clear()
        self.ax_status.axis('off')
        
        status_parts = []
        
        # Training info
        if self.training_data:
            rounds = self.training_data.get('rounds', [])
            if rounds:
                last_round = rounds[-1]
                status_parts.append(
                    f"✓ Rounds: {len(rounds)}  "
                    f"│  Accuracy: {last_round['test_accuracy']*100:.2f}%  "
                    f"│  Loss: {last_round['test_loss']:.4f}"
                )
        
        # Network info
        if self.metrics_data:
            metrics = self.metrics_data.get('rounds', [])
            if metrics:
                total_data = sum(m.get('data_sent', 0) + m.get('data_received', 0) 
                               for m in metrics)
                status_parts.append(
                    f"📡 Network: {total_data/1024/1024:.2f} MB  "
                    f"│  Clients: {self.num_clients}  "
                    f"│  Phase: {self.phase.upper()}"
                )
        
        status_text = "\n".join(status_parts) if status_parts else "Waiting for training data..."
        
        self.ax_status.text(0.5, 0.5, status_text, 
                          transform=self.ax_status.transAxes,
                          fontsize=11, ha='center', va='center',
                          color='#00FF00', fontweight='bold',
                          family='monospace',
                          bbox=dict(boxstyle='round', facecolor='black', 
                                  edgecolor='#00FF00', linewidth=2, alpha=0.8))
    
    def simulate_phase_progression(self, frame):
        """Simulate training phases"""
        self.load_data()
        
        if self.training_data:
            rounds = self.training_data.get('rounds', [])
            self.current_round = len(rounds)
        
        # Phase cycle
        cycle = frame % 180
        
        if cycle < 25:
            self.phase = "distributing"
            for i in range(self.num_clients):
                self.training_progress[i] = 0
            bandwidth = 15 + np.random.random() * 3
        elif cycle < 100:
            self.phase = "training"
            progress = (cycle - 25) / 75
            for i in range(self.num_clients):
                self.training_progress[i] = min(1.0, progress + np.random.random()*0.05)
            bandwidth = 2 + np.random.random() * 2
        elif cycle < 125:
            self.phase = "collecting"
            for i in range(self.num_clients):
                self.training_progress[i] = 1.0
            bandwidth = 12 + np.random.random() * 3
        elif cycle < 150:
            self.phase = "aggregating"
            bandwidth = 5 + np.random.random() * 2
        else:
            self.phase = "idle"
            bandwidth = 1
        
        self.bandwidth_usage.append(bandwidth)
        
        # Simulate latency
        for i in range(self.num_clients):
            self.latency_display[i] = int(10 + np.random.random() * 5)  # 10-15ms
    
    def animate(self, frame):
        """Main animation function"""
        self.simulate_phase_progression(frame)
        self.update_packets(frame)
        
        self.draw_network_topology()
        self.draw_packets()
        self.draw_phase_indicator()
        self.update_metrics_plots()
        self.update_status_panel()
    
    def show(self, interval=50):
        """Show animation"""
        anim = FuncAnimation(self.fig, self.animate, 
                           frames=None if not self.save_video else 360,
                           interval=interval, blit=False, repeat=True)
        
        if self.save_video:
            print("\n💾 Saving animation to file...")
            writer = PillowWriter(fps=20)
            anim.save('federated_learning_network.gif', writer=writer, dpi=100)
            print("✓ Saved: federated_learning_network.gif")
        
        plt.tight_layout()
        plt.show()
        return anim


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🌐 ADVANCED FEDERATED LEARNING NETWORK VISUALIZATION")
    print("="*70)
    
    print("\n✨ Features:")
    print("   ✓ Animated packet transmission with trails")
    print("   ✓ Real-time training progress bars")
    print("   ✓ Live bandwidth monitoring")
    print("   ✓ Network latency display")
    print("   ✓ Phase indicators")
    print("   ✓ Dark theme with glow effects")
    
    print("\n💡 Usage:")
    print("   1. Run this script to see simulation")
    print("   2. OR run training in other terminals for LIVE updates")
    
    import sys
    save_video = '--save' in sys.argv or '-s' in sys.argv
    
    if save_video:
        print("\n💾 Video mode enabled - will save to federated_learning_network.gif")
    
    print("\n🎨 Starting visualization...")
    print("   (Close window to exit)")
    print("="*70 + "\n")
    
    try:
        visualizer = AdvancedNetworkVisualizer(num_clients=2, save_video=save_video)
        visualizer.show(interval=50)
    except KeyboardInterrupt:
        print("\n\n⏹️  Visualization stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
