import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import json
from collections import defaultdict

def load_experiment_data(results_path):
    """Load hasil eksperimen dari CSV files"""
    # Load main results
    results_file = os.path.join(results_path, "Results_100_0.csv")
    link_file = os.path.join(results_path, "Results_100_0_link.csv")
    
    if os.path.exists(results_file):
        df_results = pd.read_csv(results_file)
    else:
        df_results = pd.DataFrame()
    
    if os.path.exists(link_file):
        df_links = pd.read_csv(link_file)
    else:
        df_links = pd.DataFrame()
    
    return df_results, df_links

def load_config_data():
    """Load configuration data untuk analisis"""
    # Load topology info
    with open('data/networkDefinition.json', 'r') as f:
        network_data = json.load(f)
    
    # Load allocation (placement) info
    with open('data/allocDefinitionGA.json', 'r') as f:
        allocation_data = json.load(f)
    
    # Load users info
    with open('data/usersDefinition.json', 'r') as f:
        users_data = json.load(f)
    
    return network_data, allocation_data, users_data

def analyze_resource_usage(df_results, allocation_data):
    """Analisis resource usage per node"""
    # Hitung jumlah module per node
    node_modules = defaultdict(int)
    for alloc in allocation_data['initialAllocation']:
        node_id = alloc['id_resource']
        node_modules[node_id] += 1
    
    # Hitung traffic per node dari results
    node_traffic = defaultdict(int)
    if not df_results.empty:
        for _, row in df_results.iterrows():
            topo_src = row['TOPO.src']
            topo_dst = row['TOPO.dst']
            node_traffic[topo_src] += 1
            if topo_src != topo_dst:
                node_traffic[topo_dst] += 1
    
    return dict(node_modules), dict(node_traffic)

def analyze_delay_metrics(df_results, df_links):
    """Analisis delay dan latency metrics"""
    delay_stats = {}
    
    if not df_results.empty:
        # Processing delay (time_out - time_in)
        df_results['processing_delay'] = df_results['time_out'] - df_results['time_in']
        
        # End-to-end delay (time_reception - time_emit)
        df_results['e2e_delay'] = df_results['time_reception'] - df_results['time_emit']
        
        delay_stats['processing_delay'] = {
            'mean': df_results['processing_delay'].mean(),
            'std': df_results['processing_delay'].std(),
            'min': df_results['processing_delay'].min(),
            'max': df_results['processing_delay'].max()
        }
        
        delay_stats['e2e_delay'] = {
            'mean': df_results['e2e_delay'].mean(),
            'std': df_results['e2e_delay'].std(),
            'min': df_results['e2e_delay'].min(),
            'max': df_results['e2e_delay'].max()
        }
    
    if not df_links.empty:
        # Network latency
        delay_stats['network_latency'] = {
            'mean': df_links['latency'].mean(),
            'std': df_links['latency'].std(),
            'min': df_links['latency'].min(),
            'max': df_links['latency'].max()
        }
    
    return delay_stats

def analyze_deadline_performance(df_results, deadline_threshold=100):
    """Analisis deadline performance"""
    deadline_stats = {}
    
    if not df_results.empty:
        # Assumsi deadline adalah waktu maksimum yang diizinkan
        df_results['meets_deadline'] = df_results['e2e_delay'] <= deadline_threshold
        
        deadline_stats = {
            'total_messages': len(df_results),
            'messages_on_time': df_results['meets_deadline'].sum(),
            'deadline_success_rate': df_results['meets_deadline'].mean() * 100,
            'average_delay': df_results['e2e_delay'].mean(),
            'deadline_threshold': deadline_threshold
        }
    
    return deadline_stats

def analyze_availability(df_results, users_data):
    """Analisis availability - berapa persen user yang berhasil mengirim traffic"""
    availability_stats = {}
    
    if not df_results.empty and users_data:
        # Total expected sources
        total_sources = len(users_data['sources'])
        
        # Active sources (yang generate traffic)
        active_apps = df_results['app'].unique()
        active_sources = len(active_apps)
        
        availability_stats = {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'availability_rate': (active_sources / total_sources) * 100 if total_sources > 0 else 0,
            'messages_per_app': df_results.groupby('app').size().to_dict()
        }
    
    return availability_stats

def plot_resource_usage(node_modules, node_traffic, save_path):
    """Plot resource usage analysis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Modules per node
    if node_modules:
        nodes = list(node_modules.keys())
        modules = list(node_modules.values())
        
        ax1.bar(range(len(nodes)), modules, alpha=0.7, color='skyblue')
        ax1.set_title('Module Distribution per Node', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Node Index')
        ax1.set_ylabel('Number of Modules')
        ax1.grid(True, alpha=0.3)
        
        # Statistics
        avg_modules = np.mean(modules)
        ax1.axhline(y=avg_modules, color='red', linestyle='--', 
                   label=f'Average: {avg_modules:.1f}')
        ax1.legend()
    
    # Plot 2: Traffic per node
    if node_traffic:
        nodes_traffic = list(node_traffic.keys())
        traffic_counts = list(node_traffic.values())
        
        ax2.bar(range(len(nodes_traffic)), traffic_counts, alpha=0.7, color='lightgreen')
        ax2.set_title('Traffic Distribution per Node', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Node Index')
        ax2.set_ylabel('Number of Messages')
        ax2.grid(True, alpha=0.3)
        
        # Statistics
        avg_traffic = np.mean(traffic_counts)
        ax2.axhline(y=avg_traffic, color='red', linestyle='--', 
                   label=f'Average: {avg_traffic:.1f}')
        ax2.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'resource_usage.png'), dpi=300, bbox_inches='tight')
    plt.close()  # Close to save memory

def plot_delay_analysis(delay_stats, df_results, save_path):
    """Plot delay analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    if not df_results.empty:
        # Plot 1: Processing delay distribution
        axes[0,0].hist(df_results['processing_delay'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0,0].set_title('Processing Delay Distribution', fontsize=12, fontweight='bold')
        axes[0,0].set_xlabel('Processing Delay (time units)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].grid(True, alpha=0.3)
        
        # Add statistics
        mean_proc = delay_stats.get('processing_delay', {}).get('mean', 0)
        axes[0,0].axvline(x=mean_proc, color='red', linestyle='--', label=f'Mean: {mean_proc:.2f}')
        axes[0,0].legend()
        
        # Plot 2: End-to-end delay distribution
        axes[0,1].hist(df_results['e2e_delay'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        axes[0,1].set_title('End-to-End Delay Distribution', fontsize=12, fontweight='bold')
        axes[0,1].set_xlabel('E2E Delay (time units)')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].grid(True, alpha=0.3)
        
        mean_e2e = delay_stats.get('e2e_delay', {}).get('mean', 0)
        axes[0,1].axvline(x=mean_e2e, color='red', linestyle='--', label=f'Mean: {mean_e2e:.2f}')
        axes[0,1].legend()
        
        # Plot 3: Delay over time
        axes[1,0].scatter(df_results['time_emit'], df_results['e2e_delay'], alpha=0.6, color='orange')
        axes[1,0].set_title('Delay vs Time', fontsize=12, fontweight='bold')
        axes[1,0].set_xlabel('Emission Time')
        axes[1,0].set_ylabel('E2E Delay')
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Delay per application
        df_results.boxplot(column='e2e_delay', by='app', ax=axes[1,1])
        axes[1,1].set_title('Delay per Application', fontsize=12, fontweight='bold')
        axes[1,1].set_xlabel('Application ID')
        axes[1,1].set_ylabel('E2E Delay')
        plt.suptitle('')  # Remove default boxplot title
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'delay_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()  # Close to save memory

def plot_deadline_performance(deadline_stats, df_results, save_path):
    """Plot deadline performance"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    if deadline_stats and not df_results.empty:
        # Plot 1: Deadline success rate (pie chart)
        on_time = deadline_stats['messages_on_time']
        late = deadline_stats['total_messages'] - on_time
        
        labels = ['On Time', 'Late']
        sizes = [on_time, late]
        colors = ['lightgreen', 'lightcoral']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title(f'Deadline Performance\n(Threshold: {deadline_stats["deadline_threshold"]} units)', 
                     fontsize=12, fontweight='bold')
        
        # Plot 2: Delay vs Deadline
        deadline_threshold = deadline_stats['deadline_threshold']
        
        ax2.hist(df_results['e2e_delay'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.axvline(x=deadline_threshold, color='red', linestyle='--', linewidth=2, 
                   label=f'Deadline: {deadline_threshold}')
        ax2.set_title('Delay Distribution vs Deadline', fontsize=12, fontweight='bold')
        ax2.set_xlabel('E2E Delay (time units)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'deadline_performance.png'), dpi=300, bbox_inches='tight')
    plt.close()  # Close to save memory

def plot_availability_analysis(availability_stats, save_path):
    """Plot availability analysis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    if availability_stats:
        # Plot 1: Overall availability
        total = availability_stats['total_sources']
        active = availability_stats['active_sources']
        inactive = total - active
        
        labels = ['Active Sources', 'Inactive Sources']
        sizes = [active, inactive]
        colors = ['lightgreen', 'lightcoral']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title(f'Source Availability\n({availability_stats["availability_rate"]:.1f}% active)', 
                     fontsize=12, fontweight='bold')
        
        # Plot 2: Messages per application
        if 'messages_per_app' in availability_stats:
            apps = list(availability_stats['messages_per_app'].keys())
            messages = list(availability_stats['messages_per_app'].values())
            
            ax2.bar(apps, messages, alpha=0.7, color='skyblue')
            ax2.set_title('Messages Generated per Application', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Application ID')
            ax2.set_ylabel('Number of Messages')
            ax2.grid(True, alpha=0.3)
            
            # Add average line
            avg_messages = np.mean(messages)
            ax2.axhline(y=avg_messages, color='red', linestyle='--', 
                       label=f'Average: {avg_messages:.1f}')
            ax2.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'availability_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()  # Close to save memory

def print_evaluation_summary(delay_stats, deadline_stats, availability_stats, node_modules, node_traffic):
    """Print comprehensive evaluation summary"""
    print("="*80)
    print("                     EXPERIMENT EVALUATION SUMMARY")
    print("="*80)
    
    # Resource Usage Summary
    print("\n📊 RESOURCE USAGE ANALYSIS")
    print("-" * 50)
    if node_modules:
        total_modules = sum(node_modules.values())
        active_nodes = len(node_modules)
        avg_modules_per_node = total_modules / active_nodes if active_nodes > 0 else 0
        
        print(f"Total Modules Deployed    : {total_modules}")
        print(f"Active Nodes              : {active_nodes}")
        print(f"Avg Modules per Node      : {avg_modules_per_node:.2f}")
        print(f"Max Modules on Single Node: {max(node_modules.values()) if node_modules else 0}")
    
    if node_traffic:
        total_traffic = sum(node_traffic.values())
        traffic_nodes = len(node_traffic)
        avg_traffic_per_node = total_traffic / traffic_nodes if traffic_nodes > 0 else 0
        
        print(f"Total Traffic Events      : {total_traffic}")
        print(f"Nodes with Traffic        : {traffic_nodes}")
        print(f"Avg Traffic per Node      : {avg_traffic_per_node:.2f}")
    
    # Delay Analysis Summary
    print("\n⏱️  DELAY PERFORMANCE ANALYSIS")
    print("-" * 50)
    if delay_stats:
        if 'processing_delay' in delay_stats:
            pd = delay_stats['processing_delay']
            print(f"Processing Delay (avg)    : {pd['mean']:.3f} ± {pd['std']:.3f}")
            print(f"Processing Delay (range)  : {pd['min']:.3f} - {pd['max']:.3f}")
        
        if 'e2e_delay' in delay_stats:
            e2e = delay_stats['e2e_delay']
            print(f"End-to-End Delay (avg)    : {e2e['mean']:.3f} ± {e2e['std']:.3f}")
            print(f"End-to-End Delay (range)  : {e2e['min']:.3f} - {e2e['max']:.3f}")
        
        if 'network_latency' in delay_stats:
            net = delay_stats['network_latency']
            print(f"Network Latency (avg)     : {net['mean']:.3f} ± {net['std']:.3f}")
            print(f"Network Latency (range)   : {net['min']:.3f} - {net['max']:.3f}")
    
    # Deadline Performance
    print("\n🎯 DEADLINE PERFORMANCE")
    print("-" * 50)
    if deadline_stats:
        print(f"Total Messages            : {deadline_stats['total_messages']}")
        print(f"Messages On Time          : {deadline_stats['messages_on_time']}")
        print(f"Deadline Success Rate     : {deadline_stats['deadline_success_rate']:.1f}%")
        print(f"Average Delay             : {deadline_stats['average_delay']:.3f}")
        print(f"Deadline Threshold        : {deadline_stats['deadline_threshold']}")
    
    # Availability Analysis
    print("\n🔄 AVAILABILITY ANALYSIS")
    print("-" * 50)
    if availability_stats:
        print(f"Total Sources Expected    : {availability_stats['total_sources']}")
        print(f"Active Sources            : {availability_stats['active_sources']}")
        print(f"Availability Rate         : {availability_stats['availability_rate']:.1f}%")
    
    print("="*80)

def main():
    """Main evaluation function"""
    # Setup
    plt.style.use('default')  # Use default style instead of seaborn
    results_path = "data/results_20250626"
    plots_path = "src/result"
    os.makedirs(plots_path, exist_ok=True)
    
    print("🔄 Loading experiment data...")
    
    # Load data
    df_results, df_links = load_experiment_data(results_path)
    network_data, allocation_data, users_data = load_config_data()
    
    if df_results.empty:
        print("❌ No experiment results found! Please run simulation first.")
        return
    
    print(f"✅ Loaded {len(df_results)} message records and {len(df_links)} link records")
    
    # Perform analysis
    print("📊 Analyzing resource usage...")
    node_modules, node_traffic = analyze_resource_usage(df_results, allocation_data)
    
    print("⏱️  Analyzing delay metrics...")
    delay_stats = analyze_delay_metrics(df_results, df_links)
    
    print("🎯 Analyzing deadline performance...")
    deadline_stats = analyze_deadline_performance(df_results, deadline_threshold=100)
    
    print("🔄 Analyzing availability...")
    availability_stats = analyze_availability(df_results, users_data)
    
    # Generate plots
    print("📈 Generating plots...")
    
    plot_resource_usage(node_modules, node_traffic, plots_path)
    plot_delay_analysis(delay_stats, df_results, plots_path)
    plot_deadline_performance(deadline_stats, df_results, plots_path)
    plot_availability_analysis(availability_stats, plots_path)
    
    # Print summary
    print_evaluation_summary(delay_stats, deadline_stats, availability_stats, 
                            node_modules, node_traffic)
    
    print(f"\n✅ Evaluation completed! Plots saved to: {plots_path}")

if __name__ == "__main__":
    main()
