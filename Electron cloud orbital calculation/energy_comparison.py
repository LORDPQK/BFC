#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparison Analysis of Theoretical Energy vs Algorithm Energy
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from advanced_orbital_solver import AdvancedOrbitalSolver
import time
import pandas as pd
import os

# Set font for better display
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EnergyComparison:
    """Energy comparison analysis class"""
    
    def __init__(self):
        # Hydrogen atom theoretical energy values (atomic units)
        self.theoretical_energies = {
            (1, 0, 0): -0.5,      # 1s orbital
            (2, 0, 0): -0.125,    # 2s orbital
            (2, 1, 0): -0.125,    # 2p_z orbital
            (2, 1, 1): -0.125,    # 2p_x orbital
            (2, 1, -1): -0.125,   # 2p_y orbital
            (3, 0, 0): -0.0556,   # 3s orbital
            (3, 1, 0): -0.0556,   # 3p orbital
            (3, 2, 0): -0.0556,   # 3d orbital
        }
    
    def get_theoretical_energy(self, n, l, m):
        """Get theoretical energy value"""
        # Hydrogen atom energy level formula: E_n = -13.6 eV / n² = -0.5 / n² (atomic units)
        return -0.5 / (n * n)
    
    def calculate_algorithm_energy(self, n, l, m, grid_size=50, iterations=400):
        """Calculate energy obtained by algorithm"""
        print(f"Calculating algorithm energy for n={n}, l={l}, m={m} orbital...")
        
        # Create solver
        solver = AdvancedOrbitalSolver(grid_size=grid_size, space_range=6.0,
                                      adaptive_grid=False, energy_minimization=True)
        
        # Use fixed parameters to avoid energy jumps
        solver.adaptive_params = {
            'decay_rate': 0.98,
            'add_strength': 0.1,
            'add_frequency': 5,
            'threshold': 1e-6
        }
        
        # Solve
        convergence_hist, energy_hist = solver.solve_with_optimization(
            n, l, m, max_iterations=iterations)
        
        # Get final energy
        if energy_hist:
            final_energy = energy_hist[-1][1]
            # Get minimum energy
            min_energy = min([e[1] for e in energy_hist])
            return final_energy, min_energy, energy_hist, solver
        else:
            return None, None, [], solver
    
    def compare_single_orbital(self, n, l, m):
        """Compare theoretical energy and algorithm energy for single orbital"""
        
        # Theoretical energy
        theoretical_energy = self.get_theoretical_energy(n, l, m)
        
        # Algorithm energy
        final_energy, min_energy, energy_hist, solver = self.calculate_algorithm_energy(n, l, m)
        
        if final_energy is None:
            print(f"Orbital n={n}, l={l}, m={m} calculation failed")
            return None
        
        # Calculate error
        final_error = abs(final_energy - theoretical_energy) / abs(theoretical_energy) * 100
        min_error = abs(min_energy - theoretical_energy) / abs(theoretical_energy) * 100
        
        result = {
            'orbital': (n, l, m),
            'theoretical': theoretical_energy,
            'algorithm_final': final_energy,
            'algorithm_min': min_energy,
            'final_error': final_error,
            'min_error': min_error,
            'energy_history': energy_hist,
            'solver': solver
        }
        
        print(f"Orbital n={n}, l={l}, m={m}:")
        print(f"  Theoretical energy: {theoretical_energy:.6f}")
        print(f"  Algorithm final energy: {final_energy:.6f} (error: {final_error:.2f}%)")
        print(f"  Algorithm minimum energy: {min_energy:.6f} (error: {min_error:.2f}%)")
        
        return result
    
    def compare_multiple_orbitals(self):
        """Compare energy for multiple orbitals"""
        
        # Orbitals to compare
        orbitals_to_compare = [
            (1, 0, 0),  # 1s
            (2, 0, 0),  # 2s
            (2, 1, 0),  # 2p_z
            (2, 1, 1),  # 2p_x
        ]
        
        results = []
        
        for n, l, m in orbitals_to_compare:
            result = self.compare_single_orbital(n, l, m)
            if result:
                results.append(result)
        
        return results
    
    def plot_energy_comparison(self, results, save_path='energy_comparison.png'):
        """Plot energy comparison charts"""
        
        if not results:
            print("No results to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Energy comparison bar chart
        ax1 = axes[0, 0]
        orbital_names = [f"{r['orbital'][0]}{['s','p','d','f'][r['orbital'][1]]}" for r in results]
        theoretical_energies = [r['theoretical'] for r in results]
        algorithm_energies = [r['algorithm_final'] for r in results]
        min_energies = [r['algorithm_min'] for r in results]
        
        x = np.arange(len(orbital_names))
        width = 0.25
        
        bars1 = ax1.bar(x - width, theoretical_energies, width, label='Theoretical', color='blue', alpha=0.7)
        bars2 = ax1.bar(x, algorithm_energies, width, label='Algorithm Final', color='red', alpha=0.7)
        bars3 = ax1.bar(x + width, min_energies, width, label='Algorithm Minimum', color='green', alpha=0.7)
        
        ax1.set_xlabel('Orbital Type')
        ax1.set_ylabel('Energy (atomic units)')
        ax1.set_title('Theoretical Energy vs Algorithm Energy Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(orbital_names)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.4f}', ha='center', va='bottom', fontsize=8)
        
        # 2. Relative error comparison
        ax2 = axes[0, 1]
        final_errors = [r['final_error'] for r in results]
        min_errors = [r['min_error'] for r in results]
        
        bars1 = ax2.bar(x - width/2, final_errors, width, label='Final Value Error', color='red', alpha=0.7)
        bars2 = ax2.bar(x + width/2, min_errors, width, label='Minimum Value Error', color='green', alpha=0.7)
        
        ax2.set_xlabel('Orbital Type')
        ax2.set_ylabel('Relative Error (%)')
        ax2.set_title('Relative Error of Algorithm Energy')
        ax2.set_xticks(x)
        ax2.set_xticklabels(orbital_names)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 3. Energy convergence history (using first orbital as example)
        ax3 = axes[1, 0]
        if results and results[0]['energy_history']:
            energy_hist = results[0]['energy_history']
            iterations = [e[0] for e in energy_hist]
            energies = [e[1] for e in energy_hist]
            theoretical = results[0]['theoretical']
            
            ax3.plot(iterations, energies, 'b-', linewidth=2, label='Algorithm Energy')
            ax3.axhline(y=theoretical, color='r', linestyle='--', linewidth=2, label='Theoretical Value')
            
            ax3.set_xlabel('Iterations')
            ax3.set_ylabel('Energy (atomic units)')
            ax3.set_title(f'Energy Convergence History ({orbital_names[0]} orbital)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Theoretical vs Algorithm scatter plot
        ax4 = axes[1, 1]
        theoretical_vals = [r['theoretical'] for r in results]
        algorithm_vals = [r['algorithm_final'] for r in results]
        min_vals = [r['algorithm_min'] for r in results]
        
        ax4.scatter(theoretical_vals, algorithm_vals, color='red', s=100, alpha=0.7, label='Final Values')
        ax4.scatter(theoretical_vals, min_vals, color='green', s=100, alpha=0.7, label='Minimum Values')
        
        # Plot ideal line y=x
        min_val = min(min(theoretical_vals), min(algorithm_vals))
        max_val = max(max(theoretical_vals), max(algorithm_vals))
        ax4.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Ideal Line y=x')
        
        ax4.set_xlabel('Theoretical Energy (atomic units)')
        ax4.set_ylabel('Algorithm Energy (atomic units)')
        ax4.set_title('Theoretical vs Algorithm Values')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Add orbital labels
        for i, (theo, algo) in enumerate(zip(theoretical_vals, algorithm_vals)):
            ax4.annotate(orbital_names[i], (theo, algo), xytext=(5, 5), 
                        textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Energy comparison chart saved to: {save_path}")
        
        return fig
    
    def create_summary_table(self, results):
        """Create energy comparison summary table"""
        
        print("\n" + "="*80)
        print("Energy Comparison Summary Table")
        print("="*80)
        print(f"{'Orbital':<8} {'Theoretical':<12} {'Algo Final':<12} {'Algo Min':<12} {'Final Err':<10} {'Min Err':<10}")
        print("-"*80)
        
        for result in results:
            n, l, m = result['orbital']
            orbital_name = f"{n}{['s','p','d','f'][l]}"
            
            print(f"{orbital_name:<8} {result['theoretical']:<12.6f} "
                  f"{result['algorithm_final']:<12.6f} {result['algorithm_min']:<12.6f} "
                  f"{result['final_error']:<10.2f}% {result['min_error']:<10.2f}%")
        
        # Calculate average error
        avg_final_error = np.mean([r['final_error'] for r in results])
        avg_min_error = np.mean([r['min_error'] for r in results])
        
        print("-"*80)
        print(f"{'Average':<8} {'':<12} {'':<12} {'':<12} {avg_final_error:<10.2f}% {avg_min_error:<10.2f}%")
        print("="*80)
        
        return avg_final_error, avg_min_error
    
    def save_to_excel(self, results, save_path='energy_comparison_data.xlsx'):
        """Save comparison results to Excel file"""
        
        if not results:
            print("No results to save")
            return
        
        # Create main summary data
        summary_data = []
        for result in results:
            n, l, m = result['orbital']
            orbital_name = f"{n}{['s','p','d','f'][l]}"
            
            summary_data.append({
                'Orbital': orbital_name,
                'n': n,
                'l': l, 
                'm': m,
                'Theoretical_Energy': result['theoretical'],
                'Algorithm_Final_Energy': result['algorithm_final'],
                'Algorithm_Min_Energy': result['algorithm_min'],
                'Final_Error_Percent': result['final_error'],
                'Min_Error_Percent': result['min_error'],
                'Final_Error_Absolute': abs(result['algorithm_final'] - result['theoretical']),
                'Min_Error_Absolute': abs(result['algorithm_min'] - result['theoretical'])
            })
        
        # Add average row
        avg_final_error = np.mean([r['final_error'] for r in results])
        avg_min_error = np.mean([r['min_error'] for r in results])
        
        summary_data.append({
            'Orbital': 'AVERAGE',
            'n': '',
            'l': '',
            'm': '',
            'Theoretical_Energy': '',
            'Algorithm_Final_Energy': '',
            'Algorithm_Min_Energy': '',
            'Final_Error_Percent': avg_final_error,
            'Min_Error_Percent': avg_min_error,
            'Final_Error_Absolute': '',
            'Min_Error_Absolute': ''
        })
        
        # Create DataFrame
        df_summary = pd.DataFrame(summary_data)
        
        # Create detailed energy history data for each orbital
        energy_history_data = []
        for result in results:
            n, l, m = result['orbital']
            orbital_name = f"{n}{['s','p','d','f'][l]}"
            
            if result['energy_history']:
                for iteration, energy in result['energy_history']:
                    energy_history_data.append({
                        'Orbital': orbital_name,
                        'n': n,
                        'l': l,
                        'm': m,
                        'Iteration': iteration,
                        'Energy': energy,
                        'Theoretical_Energy': result['theoretical'],
                        'Error_Absolute': abs(energy - result['theoretical']),
                        'Error_Percent': abs(energy - result['theoretical']) / abs(result['theoretical']) * 100
                    })
        
        df_history = pd.DataFrame(energy_history_data)
        
        # Create statistics summary
        stats_data = []
        for result in results:
            n, l, m = result['orbital']
            orbital_name = f"{n}{['s','p','d','f'][l]}"
            
            if result['energy_history']:
                energies = [e[1] for e in result['energy_history']]
                stats_data.append({
                    'Orbital': orbital_name,
                    'n': n,
                    'l': l,
                    'm': m,
                    'Theoretical_Energy': result['theoretical'],
                    'Final_Energy': result['algorithm_final'],
                    'Min_Energy': result['algorithm_min'],
                    'Max_Energy': max(energies),
                    'Mean_Energy': np.mean(energies),
                    'Std_Energy': np.std(energies),
                    'Total_Iterations': len(energies),
                    'Convergence_Range': max(energies) - min(energies)
                })
        
        df_stats = pd.DataFrame(stats_data)
        
        # Save to Excel with multiple sheets
        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # Summary sheet
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # Energy history sheet
                if not df_history.empty:
                    df_history.to_excel(writer, sheet_name='Energy_History', index=False)
                
                # Statistics sheet
                if not df_stats.empty:
                    df_stats.to_excel(writer, sheet_name='Statistics', index=False)
                
                # Create a metadata sheet
                metadata = pd.DataFrame({
                    'Parameter': ['Grid_Size', 'Iterations', 'Decay_Rate', 'Add_Strength', 'Add_Frequency', 'Threshold'],
                    'Value': [50, 400, 0.98, 0.1, 5, 1e-6],
                    'Description': [
                        'Spatial grid size for calculations',
                        'Maximum number of iterations',
                        'Decay rate for accumulation matrix',
                        'Strength of wavefunction addition',
                        'Frequency of wavefunction addition',
                        'Threshold for matrix cleanup'
                    ]
                })
                metadata.to_excel(writer, sheet_name='Parameters', index=False)
            
            print(f"✅ Excel data saved to: {save_path}")
            print(f"   📊 Sheets created: Summary, Energy_History, Statistics, Parameters")
            
        except Exception as e:
            print(f"❌ Error saving Excel file: {e}")
            print("   Trying to save as CSV instead...")
            
            # Fallback to CSV
            csv_path = save_path.replace('.xlsx', '_summary.csv')
            df_summary.to_csv(csv_path, index=False)
            print(f"   📄 CSV summary saved to: {csv_path}")
        
        return df_summary, df_history, df_stats


def main():
    """Main function"""
    print("🚀 Starting theoretical energy vs algorithm energy comparison analysis")
    print("="*60)
    
    # Create comparison analyzer
    comparator = EnergyComparison()
    
    # Compare multiple orbitals
    print("Calculating energy for multiple orbitals...")
    results = comparator.compare_multiple_orbitals()
    
    if not results:
        print("❌ No successful calculation results")
        return
    
    # Create summary table
    print("\n📊 Generating energy comparison summary...")
    avg_final_error, avg_min_error = comparator.create_summary_table(results)
    
    # Plot comparison charts
    print("\n📈 Generating energy comparison charts...")
    comparator.plot_energy_comparison(results)
    
    # Save data to Excel
    print("\n💾 Saving data to Excel...")
    df_summary, df_history, df_stats = comparator.save_to_excel(results)
    
    # Analyze results
    print(f"\n🎯 Analysis Results:")
    print(f"   Average final error: {avg_final_error:.2f}%")
    print(f"   Average minimum error: {avg_min_error:.2f}%")
    
    if avg_min_error < 5:
        print("   ✅ Algorithm accuracy is excellent!")
    elif avg_min_error < 10:
        print("   ✅ Algorithm accuracy is good!")
    else:
        print("   ⚠️  Algorithm accuracy needs improvement")
    
    print(f"\n📁 Chart saved to: energy_comparison.png")
    print(f"📊 Excel data saved to: energy_comparison_data.xlsx")
    print("🎉 Energy comparison analysis completed!")


if __name__ == "__main__":
    main()