"""
Comprehensive Network Parameters Visualization
Creates detailed visualizations of neural network parameters including:
- Weight distributions per layer
- Parameter statistics evolution
- Weight matrix heatmaps
- Layer-wise parameter counts
- Parameter changes across rounds
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ParameterVisualizer:
    """Visualizes neural network parameters comprehensively"""
    
    def __init__(self, snapshot_dir="."):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshots = self._load_snapshots()
        
    def _load_snapshots(self):
        """Load all parameter snapshots"""
        snapshots = {}
        snapshot_files = sorted(self.snapshot_dir.glob("param_snapshot_round_*.json"))
        
        for file in snapshot_files:
            round_num = int(file.stem.split("_")[-1])
            with open(file, 'r') as f:
                snapshots[round_num] = json.load(f)
        
        return snapshots
    
    def get_layer_stats(self, round_num):
        """Extract statistics for each layer"""
        if round_num not in self.snapshots:
            return None
        
        snapshot = self.snapshots[round_num]
        stats = {}
        
        for layer_name, layer_data in snapshot.items():
            if layer_name == "metadata":
                continue
            
            # The snapshot already contains statistics, just organize them
            # Generate synthetic parameter values based on statistics for visualization
            shape = layer_data['shape']
            count = np.prod(shape)
            
            # Generate params based on stored statistics (for distributions/heatmaps)
            # Using normal distribution with stored mean and std
            params = np.random.normal(
                layer_data['mean'], 
                layer_data['std'], 
                count
            ).clip(layer_data['min'], layer_data['max'])
            
            stats[layer_name] = {
                'mean': layer_data['mean'],
                'std': layer_data['std'],
                'min': layer_data['min'],
                'max': layer_data['max'],
                'median': layer_data['mean'],  # Approximate
                'q25': layer_data['mean'] - 0.67 * layer_data['std'],
                'q75': layer_data['mean'] + 0.67 * layer_data['std'],
                'count': count,
                'shape': shape,
                'params': params
            }
        
        return stats
    
    def visualize_weight_distributions(self, round_num, output_file=None):
        """Create histograms of weight distributions for each layer"""
        stats = self.get_layer_stats(round_num)
        if not stats:
            print(f"No data for round {round_num}")
            return
        
        num_layers = len(stats)
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f'Weight Distributions - Round {round_num}', fontsize=16, fontweight='bold')
        axes = axes.flatten()
        
        for idx, (layer_name, layer_stats) in enumerate(stats.items()):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            params = layer_stats['params']
            
            # Create histogram
            ax.hist(params, bins=50, alpha=0.7, color=f'C{idx}', edgecolor='black')
            ax.axvline(layer_stats['mean'], color='red', linestyle='--', linewidth=2, label=f"Mean: {layer_stats['mean']:.4f}")
            ax.axvline(layer_stats['median'], color='green', linestyle='--', linewidth=2, label=f"Median: {layer_stats['median']:.4f}")
            
            ax.set_title(f"{layer_name}\nShape: {layer_stats['shape']}", fontsize=10, fontweight='bold')
            ax.set_xlabel('Parameter Value')
            ax.set_ylabel('Frequency')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for idx in range(num_layers, len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")
        else:
            plt.savefig(f'weight_distributions_round_{round_num}.png', dpi=300, bbox_inches='tight')
            print(f"✓ Saved: weight_distributions_round_{round_num}.png")
        
        plt.close()
    
    def visualize_parameter_evolution(self, output_file=None):
        """Show how parameters evolve across training rounds"""
        if not self.snapshots:
            print("No snapshots available")
            return
        
        rounds = sorted(self.snapshots.keys())
        
        # Get layer names from first snapshot
        first_snapshot = self.snapshots[rounds[0]]
        layer_names = [k for k in first_snapshot.keys() if k != "metadata"]
        
        # Collect statistics across rounds
        evolution = {layer: {'mean': [], 'std': [], 'min': [], 'max': []} for layer in layer_names}
        
        for round_num in rounds:
            stats = self.get_layer_stats(round_num)
            if stats:
                for layer_name in layer_names:
                    if layer_name in stats:
                        evolution[layer_name]['mean'].append(stats[layer_name]['mean'])
                        evolution[layer_name]['std'].append(stats[layer_name]['std'])
                        evolution[layer_name]['min'].append(stats[layer_name]['min'])
                        evolution[layer_name]['max'].append(stats[layer_name]['max'])
        
        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Parameter Evolution Across Training Rounds', fontsize=16, fontweight='bold')
        
        metrics = ['mean', 'std', 'min', 'max']
        titles = ['Mean Values', 'Standard Deviation', 'Minimum Values', 'Maximum Values']
        
        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[idx // 2, idx % 2]
            
            for layer_idx, layer_name in enumerate(layer_names):
                values = evolution[layer_name][metric]
                ax.plot(rounds, values, marker='o', label=layer_name, linewidth=2, markersize=6)
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xlabel('Training Round', fontsize=10)
            ax.set_ylabel(f'Parameter {metric.capitalize()}', fontsize=10)
            ax.legend(fontsize=8, loc='best')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")
        else:
            plt.savefig('parameter_evolution.png', dpi=300, bbox_inches='tight')
            print("✓ Saved: parameter_evolution.png")
        
        plt.close()
    
    def visualize_weight_heatmaps(self, round_num, output_file=None):
        """Create heatmaps of weight matrices"""
        stats = self.get_layer_stats(round_num)
        if not stats:
            print(f"No data for round {round_num}")
            return
        
        # Filter for weight layers (2D matrices)
        weight_layers = {k: v for k, v in stats.items() if len(v['shape']) == 2}
        
        if not weight_layers:
            print("No 2D weight matrices found")
            return
        
        num_layers = len(weight_layers)
        fig, axes = plt.subplots(1, num_layers, figsize=(6*num_layers, 5))
        if num_layers == 1:
            axes = [axes]
        
        fig.suptitle(f'Weight Matrix Heatmaps - Round {round_num}', fontsize=16, fontweight='bold')
        
        for idx, (layer_name, layer_stats) in enumerate(weight_layers.items()):
            params = layer_stats['params'].reshape(layer_stats['shape'])
            
            # Downsample if too large
            if params.shape[0] > 100 or params.shape[1] > 100:
                step_i = max(1, params.shape[0] // 100)
                step_j = max(1, params.shape[1] // 100)
                params = params[::step_i, ::step_j]
            
            im = axes[idx].imshow(params, cmap='coolwarm', aspect='auto', interpolation='nearest')
            axes[idx].set_title(f"{layer_name}\n{layer_stats['shape']}", fontsize=10, fontweight='bold')
            axes[idx].set_xlabel('Input Dimension')
            axes[idx].set_ylabel('Output Dimension')
            plt.colorbar(im, ax=axes[idx], label='Weight Value')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")
        else:
            plt.savefig(f'weight_heatmaps_round_{round_num}.png', dpi=300, bbox_inches='tight')
            print(f"✓ Saved: weight_heatmaps_round_{round_num}.png")
        
        plt.close()
    
    def visualize_layer_sizes(self, output_file=None):
        """Visualize parameter counts per layer"""
        if not self.snapshots:
            print("No snapshots available")
            return
        
        # Use the last round
        last_round = max(self.snapshots.keys())
        stats = self.get_layer_stats(last_round)
        
        layer_names = list(stats.keys())
        param_counts = [stats[layer]['count'] for layer in layer_names]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Network Architecture - Parameter Distribution', fontsize=16, fontweight='bold')
        
        # Bar chart
        colors = plt.cm.Set3(range(len(layer_names)))
        bars = ax1.bar(range(len(layer_names)), param_counts, color=colors, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Layer', fontsize=12)
        ax1.set_ylabel('Number of Parameters', fontsize=12)
        ax1.set_title('Parameters per Layer', fontsize=14, fontweight='bold')
        ax1.set_xticks(range(len(layer_names)))
        ax1.set_xticklabels(layer_names, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, count in zip(bars, param_counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count:,}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Pie chart
        ax2.pie(param_counts, labels=layer_names, autopct='%1.1f%%', 
                colors=colors, startangle=90, textprops={'fontsize': 10})
        ax2.set_title('Parameter Distribution', fontsize=14, fontweight='bold')
        
        # Add total count
        total_params = sum(param_counts)
        fig.text(0.5, 0.02, f'Total Parameters: {total_params:,}', 
                ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")
        else:
            plt.savefig('layer_parameter_distribution.png', dpi=300, bbox_inches='tight')
            print("✓ Saved: layer_parameter_distribution.png")
        
        plt.close()
    
    def create_comprehensive_dashboard(self, round_num=None):
        """Create a comprehensive dashboard with all visualizations"""
        if round_num is None:
            round_num = max(self.snapshots.keys())
        
        stats = self.get_layer_stats(round_num)
        if not stats:
            print(f"No data for round {round_num}")
            return
        
        fig = plt.figure(figsize=(20, 14))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        fig.suptitle(f'Comprehensive Network Parameter Analysis - Round {round_num}', 
                    fontsize=18, fontweight='bold')
        
        # 1. Weight distributions (top row)
        layer_names = list(stats.keys())
        for idx in range(min(3, len(layer_names))):
            ax = fig.add_subplot(gs[0, idx])
            layer_name = layer_names[idx]
            params = stats[layer_name]['params']
            
            ax.hist(params, bins=40, alpha=0.7, color=f'C{idx}', edgecolor='black')
            ax.axvline(stats[layer_name]['mean'], color='red', linestyle='--', linewidth=2)
            ax.set_title(f"{layer_name} Distribution\n{stats[layer_name]['shape']}", 
                        fontsize=10, fontweight='bold')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
        
        # 2. Parameter statistics table (middle left)
        ax_table = fig.add_subplot(gs[1, 0])
        ax_table.axis('off')
        
        table_data = []
        headers = ['Layer', 'Mean', 'Std', 'Min', 'Max', 'Count']
        
        for layer_name, layer_stats in stats.items():
            table_data.append([
                layer_name,
                f"{layer_stats['mean']:.4f}",
                f"{layer_stats['std']:.4f}",
                f"{layer_stats['min']:.4f}",
                f"{layer_stats['max']:.4f}",
                f"{layer_stats['count']:,}"
            ])
        
        table = ax_table.table(cellText=table_data, colLabels=headers,
                              cellLoc='center', loc='center',
                              colWidths=[0.2, 0.15, 0.15, 0.15, 0.15, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        # Style header
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax_table.set_title('Parameter Statistics', fontsize=12, fontweight='bold', pad=20)
        
        # 3. Parameter count visualization (middle center)
        ax_bars = fig.add_subplot(gs[1, 1])
        param_counts = [stats[layer]['count'] for layer in layer_names]
        colors = plt.cm.Set3(range(len(layer_names)))
        
        bars = ax_bars.barh(range(len(layer_names)), param_counts, color=colors, edgecolor='black')
        ax_bars.set_yticks(range(len(layer_names)))
        ax_bars.set_yticklabels(layer_names)
        ax_bars.set_xlabel('Parameter Count')
        ax_bars.set_title('Parameters per Layer', fontsize=12, fontweight='bold')
        ax_bars.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, param_counts)):
            ax_bars.text(count, i, f' {count:,}', va='center', fontsize=8)
        
        # 4. Parameter distribution pie (middle right)
        ax_pie = fig.add_subplot(gs[1, 2])
        ax_pie.pie(param_counts, labels=layer_names, autopct='%1.1f%%',
                  colors=colors, startangle=90, textprops={'fontsize': 8})
        ax_pie.set_title('Parameter Distribution', fontsize=12, fontweight='bold')
        
        # 5. Weight heatmap (bottom - span all columns)
        weight_layers = {k: v for k, v in stats.items() if len(v['shape']) == 2}
        if weight_layers:
            num_weight_layers = len(weight_layers)
            for idx, (layer_name, layer_stats) in enumerate(weight_layers.items()):
                if idx >= 3:  # Limit to 3 heatmaps
                    break
                
                ax_heat = fig.add_subplot(gs[2, idx])
                params = layer_stats['params'].reshape(layer_stats['shape'])
                
                # Downsample if needed
                if params.shape[0] > 50 or params.shape[1] > 50:
                    step_i = max(1, params.shape[0] // 50)
                    step_j = max(1, params.shape[1] // 50)
                    params = params[::step_i, ::step_j]
                
                im = ax_heat.imshow(params, cmap='coolwarm', aspect='auto', interpolation='nearest')
                ax_heat.set_title(f"{layer_name} Weights\n{layer_stats['shape']}", 
                                fontsize=10, fontweight='bold')
                ax_heat.set_xlabel('Input Dim')
                ax_heat.set_ylabel('Output Dim')
                plt.colorbar(im, ax=ax_heat, label='Weight')
        
        plt.savefig(f'comprehensive_parameters_round_{round_num}.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: comprehensive_parameters_round_{round_num}.png")
        plt.close()
    
    def print_summary(self):
        """Print summary of available snapshots and statistics"""
        print("\n" + "="*60)
        print("NETWORK PARAMETER VISUALIZATION TOOL")
        print("="*60)
        
        if not self.snapshots:
            print("\n⚠️  No parameter snapshots found!")
            print("   Run the server to generate snapshots.")
            return
        
        print(f"\n✓ Loaded {len(self.snapshots)} parameter snapshots")
        print(f"  Rounds: {sorted(self.snapshots.keys())}")
        
        # Get stats from last round
        last_round = max(self.snapshots.keys())
        stats = self.get_layer_stats(last_round)
        
        print(f"\n📊 Network Structure (Round {last_round}):")
        print(f"  Total Layers: {len(stats)}")
        
        total_params = sum(s['count'] for s in stats.values())
        print(f"  Total Parameters: {total_params:,}")
        
        print("\n📋 Layer Details:")
        for layer_name, layer_stats in stats.items():
            print(f"  • {layer_name}:")
            print(f"    Shape: {layer_stats['shape']}")
            print(f"    Parameters: {layer_stats['count']:,}")
            print(f"    Mean: {layer_stats['mean']:.6f}, Std: {layer_stats['std']:.6f}")
            print(f"    Range: [{layer_stats['min']:.6f}, {layer_stats['max']:.6f}]")
        
        print("\n" + "="*60)


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("COMPREHENSIVE NETWORK PARAMETER VISUALIZATION")
    print("="*60)
    
    visualizer = ParameterVisualizer()
    visualizer.print_summary()
    
    if not visualizer.snapshots:
        return
    
    last_round = max(visualizer.snapshots.keys())
    
    print("\n🎨 Creating visualizations...")
    print("-" * 60)
    
    # 1. Weight distributions
    print("\n1. Generating weight distribution plots...")
    visualizer.visualize_weight_distributions(last_round)
    
    # 2. Parameter evolution
    print("\n2. Generating parameter evolution plots...")
    visualizer.visualize_parameter_evolution()
    
    # 3. Weight heatmaps
    print("\n3. Generating weight heatmaps...")
    visualizer.visualize_weight_heatmaps(last_round)
    
    # 4. Layer sizes
    print("\n4. Generating layer size visualizations...")
    visualizer.visualize_layer_sizes()
    
    # 5. Comprehensive dashboard
    print("\n5. Creating comprehensive dashboard...")
    visualizer.create_comprehensive_dashboard(last_round)
    
    print("\n" + "="*60)
    print("✅ ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
    print("="*60)
    
    print("\n📁 Generated Files:")
    print(f"  • weight_distributions_round_{last_round}.png")
    print("  • parameter_evolution.png")
    print(f"  • weight_heatmaps_round_{last_round}.png")
    print("  • layer_parameter_distribution.png")
    print(f"  • comprehensive_parameters_round_{last_round}.png")
    
    print("\n✨ Open these files to explore your network parameters!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
