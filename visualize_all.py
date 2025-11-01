"""
Comprehensive Federated Learning Results Visualization

This script creates a single comprehensive dashboard combining:
- Training metrics (accuracy, loss)
- Performance metrics (timing, network)
- Client participation

Usage:
    python visualize_all.py
"""

import json
import matplotlib.pyplot as plt
import os

def load_data():
    """Load all available data files"""
    data = {}
    
    # Load training history
    if os.path.exists('training_history.json'):
        with open('training_history.json', 'r') as f:
            data['training'] = json.load(f)
    else:
        print("Warning: training_history.json not found")
        data['training'] = None
    
    # Load performance metrics
    if os.path.exists('performance_metrics.json'):
        with open('performance_metrics.json', 'r') as f:
            data['metrics'] = json.load(f)
    else:
        print("Warning: performance_metrics.json not found")
        data['metrics'] = None
    
    return data

def create_comprehensive_dashboard(data):
    """Create a comprehensive dashboard with all metrics"""
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    training = data['training']
    metrics = data['metrics']
    
    if training:
        rounds = training['rounds']
        accuracies = training['accuracies']
        losses = training['losses']
        num_clients = training['num_clients']
        
        # 1. Accuracy (large plot - top row)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(rounds, accuracies, 'b-o', linewidth=3, markersize=10, label='Test Accuracy')
        ax1.set_xlabel('Round', fontsize=12)
        ax1.set_ylabel('Accuracy (%)', fontsize=12)
        ax1.set_title('Model Accuracy Over Training Rounds', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([0, 100])
        ax1.legend(fontsize=11)
        
        # Add annotations for key points
        max_acc_idx = accuracies.index(max(accuracies))
        ax1.annotate(f'Best: {max(accuracies):.2f}%', 
                    xy=(rounds[max_acc_idx], accuracies[max_acc_idx]),
                    xytext=(10, -20), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # 2. Training Stats Summary
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        stats_text = f"""
        Training Summary
        {'='*30}
        
        Rounds: {len(rounds)}
        
        Accuracy:
          Initial: {accuracies[0]:.2f}%
          Final: {accuracies[-1]:.2f}%
          Best: {max(accuracies):.2f}%
          Δ: +{accuracies[-1]-accuracies[0]:.2f}%
        
        Loss:
          Initial: {losses[0]:.4f}
          Final: {losses[-1]:.4f}
          Best: {min(losses):.4f}
        
        Clients:
          Avg: {sum(num_clients)/len(num_clients):.1f}
          Total Updates: {sum(num_clients)}
        """
        ax2.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
                verticalalignment='center')
        
        # 3. Loss over rounds
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(rounds, losses, 'r-o', linewidth=2, markersize=8)
        ax3.set_xlabel('Round', fontsize=11)
        ax3.set_ylabel('Loss', fontsize=11)
        ax3.set_title('Training Loss', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # 4. Client participation
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.bar(rounds, num_clients, color='green', alpha=0.7, edgecolor='black')
        ax4.set_xlabel('Round', fontsize=11)
        ax4.set_ylabel('Clients', fontsize=11)
        ax4.set_title('Client Participation', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Accuracy improvement
        ax5 = fig.add_subplot(gs[1, 2])
        acc_diff = [0] + [accuracies[i] - accuracies[i-1] for i in range(1, len(accuracies))]
        colors = ['green' if x >= 0 else 'red' for x in acc_diff]
        ax5.bar(rounds, acc_diff, color=colors, alpha=0.7, edgecolor='black')
        ax5.set_xlabel('Round', fontsize=11)
        ax5.set_ylabel('Δ Accuracy (%)', fontsize=11)
        ax5.set_title('Accuracy Change', fontsize=12, fontweight='bold')
        ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax5.grid(True, alpha=0.3, axis='y')
    
    if metrics:
        # 6. Round duration
        ax6 = fig.add_subplot(gs[2, 0])
        ax6.plot(metrics['rounds'], metrics['round_durations'], 'b-o', linewidth=2, markersize=6)
        ax6.set_xlabel('Round', fontsize=11)
        ax6.set_ylabel('Time (s)', fontsize=11)
        ax6.set_title('Round Duration', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        
        avg_dur = sum(metrics['round_durations']) / len(metrics['round_durations'])
        ax6.axhline(y=avg_dur, color='r', linestyle='--', alpha=0.5)
        
        # 7. Network traffic
        ax7 = fig.add_subplot(gs[2, 1])
        network_mb = [b/1024/1024 for b in metrics['network_overhead']]
        ax7.bar(metrics['rounds'], network_mb, color='orange', alpha=0.7, edgecolor='black')
        ax7.set_xlabel('Round', fontsize=11)
        ax7.set_ylabel('Data (MB)', fontsize=11)
        ax7.set_title('Network Traffic', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 8. Performance summary
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        
        total_duration = sum(metrics['round_durations'])
        total_traffic = sum(metrics['network_overhead']) / 1024 / 1024
        avg_agg = sum(metrics['aggregation_times']) / len(metrics['aggregation_times']) if metrics['aggregation_times'] else 0
        avg_eval = sum(metrics['evaluation_times']) / len(metrics['evaluation_times']) if metrics['evaluation_times'] else 0
        
        perf_text = f"""
        Performance Summary
        {'='*28}
        
        Timing:
          Total: {total_duration:.1f}s
          Avg/Round: {total_duration/len(metrics['rounds']):.1f}s
          Avg Agg: {avg_agg:.3f}s
          Avg Eval: {avg_eval:.1f}s
        
        Network:
          Total: {total_traffic:.2f} MB
          Avg/Round: {total_traffic/len(metrics['rounds']):.2f} MB
          
        Efficiency:
          Throughput: {total_traffic/total_duration*1024:.1f} KB/s
        """
        ax8.text(0.1, 0.5, perf_text, fontsize=10, family='monospace',
                verticalalignment='center')
    
    plt.suptitle('Federated Learning - Complete Training Dashboard', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    plt.savefig('complete_dashboard.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: complete_dashboard.png")
    plt.show()

def main():
    """Main function"""
    print("="*60)
    print("Comprehensive Federated Learning Visualization")
    print("="*60)
    
    # Load data
    data = load_data()
    
    if data['training'] is None and data['metrics'] is None:
        print("\nError: No data files found!")
        print("Run the server first to generate training data.")
        return
    
    print("\n✓ Data loaded successfully")
    if data['training']:
        print(f"  - Training history: {len(data['training']['rounds'])} rounds")
    if data['metrics']:
        print(f"  - Performance metrics: {len(data['metrics']['rounds'])} rounds")
    
    # Create comprehensive dashboard
    print("\nCreating comprehensive dashboard...")
    create_comprehensive_dashboard(data)
    
    print("\n✓ Complete dashboard created successfully!")
    print("\nGenerated file:")
    print("  - complete_dashboard.png")

if __name__ == "__main__":
    main()
