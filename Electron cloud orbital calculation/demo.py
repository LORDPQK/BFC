#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子云轨道计算器演示脚本
展示累积-衰减算法计算电子云轨道的完整流程
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import time
import os
import pandas as pd
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from orbital_calculator import OrbitalCalculator
from advanced_orbital_solver import AdvancedOrbitalSolver

def demo_basic_calculation():
    """演示基础计算功能"""
    print("=== 基础电子云轨道计算演示 ===")
    
    # 创建计算器
    calc = OrbitalCalculator(grid_size=60, space_range=6.0)
    
    # 计算1s轨道
    print("\n1. 计算氢原子1s轨道")
    start_time = time.time()
    
    history = calc.iterative_solve(n=1, l=0, m=0, 
                                  iterations=200,
                                  add_strength=0.1,
                                  decay_rate=0.98,
                                  add_frequency=5)
    
    end_time = time.time()
    print(f"计算耗时: {end_time - start_time:.2f} 秒")
    
    # 可视化结果
    print("2. 生成可视化结果...")
    
    # XY切片
    fig1 = calc.visualize_orbital('xy', calc.grid_size//2, "1s Orbital - XY Slice")
    plt.savefig('电子云轨道计算/demo_1s_xy.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    # 3D可视化
    fig2 = calc.visualize_3d_orbital(threshold_percentile=85, alpha=0.5)
    plt.savefig('电子云轨道计算/demo_1s_3d.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    # 与理论比较
    fig3, correlation = calc.compare_with_theory(1, 0, 0)
    plt.savefig('电子云轨道计算/demo_1s_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"3. 与理论值比较: 相关系数 = {correlation:.4f}")
    
    return calc, correlation

def demo_multiple_orbitals():
    """演示多轨道计算"""
    print("\n=== 多轨道计算演示 ===")
    
    calc = OrbitalCalculator(grid_size=50, space_range=8.0)
    
    # 要计算的轨道列表
    orbitals = [
        (1, 0, 0, "1s"),
        (2, 0, 0, "2s"), 
        (2, 1, 0, "2p_z"),
        (2, 1, 1, "2p_x")
    ]
    
    results = {}
    
    for n, l, m, name in orbitals:
        print(f"\n计算 {name} 轨道 (n={n}, l={l}, m={m})...")
        
        start_time = time.time()
        history = calc.iterative_solve(n, l, m, 
                                      iterations=300,
                                      add_strength=0.12,
                                      decay_rate=0.98,
                                      add_frequency=4)
        end_time = time.time()
        
        # 保存可视化
        fig = calc.visualize_orbital('xy', calc.grid_size//2, f"{name} Orbital")
        plt.savefig(f'电子云轨道计算/demo_{name}_orbital.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # 与理论比较
        fig, correlation = calc.compare_with_theory(n, l, m)
        plt.close()
        
        results[name] = {
            'time': end_time - start_time,
            'correlation': correlation,
            'final_points': history[-1][1] if history else 0
        }
        
        print(f"  耗时: {end_time - start_time:.2f}秒, 相关系数: {correlation:.4f}")
    
    return results

def demo_convergence_analysis():
    """演示收敛性分析"""
    print("\n=== 收敛性分析演示 ===")
    
    calc = OrbitalCalculator(grid_size=40, space_range=5.0)
    
    # 测试不同参数的收敛性
    param_sets = [
        {'decay_rate': 0.95, 'add_strength': 0.2, 'name': 'Fast'},
        {'decay_rate': 0.98, 'add_strength': 0.1, 'name': 'Balanced'},
        {'decay_rate': 0.99, 'add_strength': 0.05, 'name': 'Stable'},
    ]
    
    plt.figure(figsize=(15, 5))
    convergence_data = {}
    
    for i, params in enumerate(param_sets):
        print(f"测试参数组合: {params['name']}")
        
        history = calc.iterative_solve(1, 0, 0, iterations=200,
                                      decay_rate=params['decay_rate'],
                                      add_strength=params['add_strength'],
                                      add_frequency=5)
        
        # 保存收敛数据
        convergence_data[params['name']] = {
            'history': history,
            'decay_rate': params['decay_rate'],
            'add_strength': params['add_strength']
        }
        
        # 绘制收敛曲线
        plt.subplot(1, 3, i+1)
        iterations = [h[0] for h in history]
        max_values = [h[2] for h in history]
        
        plt.plot(iterations, max_values, linewidth=2, label=params['name'])
        plt.xlabel('Iterations')
        plt.ylabel('Max Value')
        plt.title(f"{params['name']} Convergence")
        plt.grid(True, alpha=0.3)
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('电子云轨道计算/demo_convergence_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("收敛性分析完成")
    return convergence_data

def demo_advanced_features():
    """演示高级功能"""
    print("\n=== 高级功能演示 ===")
    
    # 创建高级求解器
    solver = AdvancedOrbitalSolver(grid_size=50, space_range=6.0,
                                  adaptive_grid=True, energy_minimization=True)
    
    print("1. 自适应网格优化求解...")
    
    # 🔧 使用固定参数，不让算法瞎调整
    solver.adaptive_params = {
        'decay_rate': 0.98,      # 固定
        'add_strength': 0.1,     # 固定  
        'add_frequency': 5,      # 固定
        'threshold': 1e-6        # 固定
    }
    print("✅ 已禁用自适应调整，使用固定参数")

    
    start_time = time.time()
    
    convergence_hist, energy_hist = solver.solve_with_optimization(2, 1, 0, max_iterations=400)
    
    end_time = time.time()
    print(f"   优化求解耗时: {end_time - start_time:.2f} 秒")
    
    # 高级可视化
    print("2. 生成高级可视化...")
    fig = solver.advanced_visualization(2, 1, 0, '电子云轨道计算/demo_advanced_2p.png')
    plt.close()
    
    # 多轨道叠加
    print("3. 多轨道叠加态计算...")
    orbital_configs = [(2, 0, 0), (2, 1, 0), (2, 1, 1)]
    weights = [0.4, 0.4, 0.2]
    
    solver.multi_orbital_superposition(orbital_configs, weights)
    
    # 可视化叠加态
    fig = solver.advanced_visualization(2, 1, 0, '电子云轨道计算/demo_superposition.png')
    plt.close()
    
    print("高级功能演示完成")
    
    return solver

def calculate_radial_distribution(calc, n, l, m, orbital_name):
    """计算径向分布数据"""
    # 获取当前轨道的累积矩阵
    accumulation = calc.accumulation_matrix
    
    # 计算径向距离
    r = calc.r
    
    # 创建径向分布数据
    max_r = calc.space_range
    r_points = np.linspace(0, max_r, 100)
    radial_density = []
    
    for r_val in r_points:
        # 找到距离r_val最近的点
        mask = (r >= r_val - 0.1) & (r <= r_val + 0.1)
        if np.any(mask):
            density = np.mean(accumulation[mask])
        else:
            density = 0
        radial_density.append(density)
    
    return r_points, radial_density

def save_demo_data_to_excel(basic_results, multi_results, solver, convergence_data=None, save_path='demo_results.xlsx'):
    """保存演示数据到Excel文件"""
    print("\n=== 保存数据到Excel ===")
    
    try:
        # 1. 基础结果汇总表
        summary_data = []
        
        # 添加基础1s轨道结果
        summary_data.append({
            'Test_Type': 'Basic_1s',
            'Orbital': '1s',
            'n': 1,
            'l': 0,
            'm': 0,
            'Correlation': basic_results,
            'Computation_Time_s': '',
            'Final_Points': '',
            'Grid_Size': 60,
            'Space_Range': 6.0,
            'Iterations': 200,
            'Add_Strength': 0.1,
            'Decay_Rate': 0.98,
            'Add_Frequency': 5,
            'Quality_Rating': 'Excellent' if basic_results > 0.9 else 'Good' if basic_results > 0.8 else 'Fair'
        })
        
        # 添加多轨道结果
        orbital_mapping = {
            '1s': (1, 0, 0),
            '2s': (2, 0, 0),
            '2p_z': (2, 1, 0),
            '2p_x': (2, 1, 1)
        }
        
        for orbital_name, result in multi_results.items():
            n, l, m = orbital_mapping.get(orbital_name, (0, 0, 0))
            summary_data.append({
                'Test_Type': 'Multi_Orbital',
                'Orbital': orbital_name,
                'n': n,
                'l': l,
                'm': m,
                'Correlation': result['correlation'],
                'Computation_Time_s': result['time'],
                'Final_Points': result['final_points'],
                'Grid_Size': 50,
                'Space_Range': 8.0,
                'Iterations': 300,
                'Add_Strength': 0.12,
                'Decay_Rate': 0.98,
                'Add_Frequency': 4,
                'Quality_Rating': 'Excellent' if result['correlation'] > 0.9 else 'Good' if result['correlation'] > 0.8 else 'Fair'
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        # 2. 性能统计表
        correlations = [basic_results] + [r['correlation'] for r in multi_results.values()]
        times = [r['time'] for r in multi_results.values()]
        
        stats_data = [{
            'Metric': 'Average_Correlation',
            'Value': np.mean(correlations),
            'Description': 'Average correlation with theoretical values'
        }, {
            'Metric': 'Min_Correlation',
            'Value': np.min(correlations),
            'Description': 'Minimum correlation achieved'
        }, {
            'Metric': 'Max_Correlation',
            'Value': np.max(correlations),
            'Description': 'Maximum correlation achieved'
        }, {
            'Metric': 'Average_Time',
            'Value': np.mean(times),
            'Description': 'Average computation time (seconds)'
        }, {
            'Metric': 'Total_Time',
            'Value': np.sum(times),
            'Description': 'Total computation time (seconds)'
        }, {
            'Metric': 'Total_Orbitals',
            'Value': len(multi_results) + 1,
            'Description': 'Total number of orbitals calculated'
        }]
        
        df_stats = pd.DataFrame(stats_data)
        
        # 3. 高级求解器数据（如果有的话）
        advanced_data = []
        if hasattr(solver, 'convergence_history') and solver.convergence_history:
            for iteration, remaining_points, max_value in solver.convergence_history:
                advanced_data.append({
                    'Iteration': iteration,
                    'Remaining_Points': remaining_points,
                    'Max_Value': max_value,
                    'Solver_Type': 'Advanced',
                    'Orbital': '2p_z',
                    'n': 2,
                    'l': 1,
                    'm': 0
                })
        
        df_advanced = pd.DataFrame(advanced_data)
        
        # 4. 能量历史数据（如果有的话）
        energy_data = []
        if hasattr(solver, 'energy_history') and solver.energy_history:
            for iteration, energy in solver.energy_history:
                energy_data.append({
                    'Iteration': iteration,
                    'Energy': energy,
                    'Solver_Type': 'Advanced_Energy',
                    'Orbital': '2p_z',
                    'n': 2,
                    'l': 1,
                    'm': 0
                })
        
        df_energy = pd.DataFrame(energy_data)
        
        # 5. 算法参数配置表
        config_data = [{
            'Parameter': 'Basic_Grid_Size',
            'Value': 60,
            'Description': 'Grid size for basic 1s calculation'
        }, {
            'Parameter': 'Basic_Space_Range',
            'Value': 6.0,
            'Description': 'Space range for basic 1s calculation'
        }, {
            'Parameter': 'Multi_Grid_Size',
            'Value': 50,
            'Description': 'Grid size for multi-orbital calculations'
        }, {
            'Parameter': 'Multi_Space_Range',
            'Value': 8.0,
            'Description': 'Space range for multi-orbital calculations'
        }, {
            'Parameter': 'Advanced_Grid_Size',
            'Value': 50,
            'Description': 'Grid size for advanced solver'
        }, {
            'Parameter': 'Advanced_Space_Range',
            'Value': 6.0,
            'Description': 'Space range for advanced solver'
        }, {
            'Parameter': 'Convergence_Grid_Size',
            'Value': 40,
            'Description': 'Grid size for convergence analysis'
        }, {
            'Parameter': 'Convergence_Space_Range',
            'Value': 5.0,
            'Description': 'Space range for convergence analysis'
        }]
        
        df_config = pd.DataFrame(config_data)
        
        # 6. 收敛分析数据（如果有的话）
        convergence_analysis_data = []
        if convergence_data:
            for param_name, data in convergence_data.items():
                history = data['history']
                for iteration, remaining_points, max_value in history:
                    convergence_analysis_data.append({
                        'Parameter_Set': param_name,
                        'Decay_Rate': data['decay_rate'],
                        'Add_Strength': data['add_strength'],
                        'Iteration': iteration,
                        'Remaining_Points': remaining_points,
                        'Max_Value': max_value,
                        'Orbital': '1s',
                        'n': 1,
                        'l': 0,
                        'm': 0
                    })
        
        df_convergence_analysis = pd.DataFrame(convergence_analysis_data)
        
        # 7. 径向分布数据
        radial_data = []
        # 为每个轨道计算径向分布（使用多轨道计算的计算器）
        calc_multi = OrbitalCalculator(grid_size=50, space_range=8.0)
        
        for orbital_name in multi_results.keys():
            n, l, m = orbital_mapping.get(orbital_name, (0, 0, 0))
            if n > 0:  # 有效轨道
                # 重新计算轨道以获取径向分布
                calc_multi.iterative_solve(n, l, m, iterations=100, 
                                         add_strength=0.12, decay_rate=0.98, add_frequency=4)
                
                r_points, radial_density = calculate_radial_distribution(calc_multi, n, l, m, orbital_name)
                
                for r_val, density in zip(r_points, radial_density):
                    radial_data.append({
                        'Orbital': orbital_name,
                        'n': n,
                        'l': l,
                        'm': m,
                        'Radius_Bohr': r_val,
                        'Radial_Density': density,
                        'Normalized_Radius': r_val / calc_multi.space_range
                    })
        
        df_radial = pd.DataFrame(radial_data)
        
        # 8. 元数据表
        metadata = [{
            'Property': 'Generation_Time',
            'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Description': 'When this data was generated'
        }, {
            'Property': 'Algorithm_Type',
            'Value': 'Accumulation-Decay',
            'Description': 'Type of algorithm used'
        }, {
            'Property': 'Total_Calculations',
            'Value': len(multi_results) + 1,
            'Description': 'Total number of orbital calculations performed'
        }, {
            'Property': 'Python_Version',
            'Value': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            'Description': 'Python version used'
        }, {
            'Property': 'Convergence_Tests',
            'Value': len(convergence_data) if convergence_data else 0,
            'Description': 'Number of convergence parameter sets tested'
        }, {
            'Property': 'Radial_Points',
            'Value': len(df_radial) // len(multi_results) if len(multi_results) > 0 else 0,
            'Description': 'Number of radial points per orbital'
        }]
        
        df_metadata = pd.DataFrame(metadata)
        
        # 保存到Excel文件
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            # 主要结果
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # 统计数据
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
            
            # 高级求解器收敛历史
            if not df_advanced.empty:
                df_advanced.to_excel(writer, sheet_name='Advanced_Convergence', index=False)
            
            # 能量历史
            if not df_energy.empty:
                df_energy.to_excel(writer, sheet_name='Energy_History', index=False)
            
            # 收敛分析数据
            if not df_convergence_analysis.empty:
                df_convergence_analysis.to_excel(writer, sheet_name='Convergence_Analysis', index=False)
            
            # 径向分布数据
            if not df_radial.empty:
                df_radial.to_excel(writer, sheet_name='Radial_Distribution', index=False)
            
            # 配置参数
            df_config.to_excel(writer, sheet_name='Configuration', index=False)
            
            # 元数据
            df_metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        print(f"✅ Excel数据已保存到: {save_path}")
        
        # 显示保存的工作表
        sheets = ['Summary', 'Statistics', 'Configuration', 'Metadata']
        if not df_advanced.empty:
            sheets.append('Advanced_Convergence')
        if not df_energy.empty:
            sheets.append('Energy_History')
        if not df_convergence_analysis.empty:
            sheets.append('Convergence_Analysis')
        if not df_radial.empty:
            sheets.append('Radial_Distribution')
        
        print(f"📊 包含工作表: {', '.join(sheets)}")
        
        return df_summary, df_stats, df_advanced, df_energy, df_convergence_analysis, df_radial
        
    except Exception as e:
        print(f"❌ 保存Excel文件时出错: {e}")
        print("   尝试保存为CSV格式...")
        
        # 备用CSV保存
        try:
            df_summary.to_csv(save_path.replace('.xlsx', '_summary.csv'), index=False)
            df_stats.to_csv(save_path.replace('.xlsx', '_stats.csv'), index=False)
            print(f"📄 CSV文件已保存")
        except Exception as csv_error:
            print(f"❌ CSV保存也失败: {csv_error}")
        
        return None, None, None, None

def create_summary_report(basic_results, multi_results, solver):
    """创建总结报告"""
    print("\n=== 生成总结报告 ===")
    
    # 创建总结图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 相关系数对比
    ax1 = axes[0, 0]
    orbitals = list(multi_results.keys())
    correlations = [multi_results[orb]['correlation'] for orb in orbitals]
    
    bars = ax1.bar(orbitals, correlations, color=['red', 'blue', 'green', 'orange'])
    ax1.set_ylabel('Correlation with Theory')
    ax1.set_title('Accuracy Comparison')
    ax1.set_ylim(0, 1)
    
    # 添加数值标签
    for bar, corr in zip(bars, correlations):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{corr:.3f}', ha='center', va='bottom')
    
    # 2. 计算时间对比
    ax2 = axes[0, 1]
    times = [multi_results[orb]['time'] for orb in orbitals]
    
    bars = ax2.bar(orbitals, times, color=['red', 'blue', 'green', 'orange'])
    ax2.set_ylabel('Computation Time (s)')
    ax2.set_title('Performance Comparison')
    
    for bar, time_val in zip(bars, times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{time_val:.1f}s', ha='center', va='bottom')
    
    # 3. 收敛历史（如果有的话）
    ax3 = axes[1, 0]
    if hasattr(solver, 'convergence_history') and solver.convergence_history:
        iterations = [h[0] for h in solver.convergence_history]
        max_values = [h[2] for h in solver.convergence_history]
        ax3.plot(iterations, max_values, 'b-', linewidth=2)
        ax3.set_xlabel('Iterations')
        ax3.set_ylabel('Max Value')
        ax3.set_title('Advanced Solver Convergence')
        ax3.grid(True, alpha=0.3)
    
    # 4. 能量收敛（如果有的话）
    ax4 = axes[1, 1]
    if hasattr(solver, 'energy_history') and solver.energy_history:
        iterations = [h[0] for h in solver.energy_history]
        energies = [h[1] for h in solver.energy_history]
        ax4.plot(iterations, energies, 'r-', linewidth=2)
        ax4.set_xlabel('Iterations')
        ax4.set_ylabel('Energy')
        ax4.set_title('Energy Minimization')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('demo_summary_report.png', dpi=200, bbox_inches='tight')
    plt.close()
    
    # 打印文字报告
    print("\n" + "="*60)
    print("电子云轨道计算器演示总结报告")
    print("="*60)
    
    print(f"\n基础1s轨道计算:")
    print(f"  相关系数: {basic_results:.4f}")
    print(f"  评价: {'优秀' if basic_results > 0.9 else '良好' if basic_results > 0.8 else '一般'}")
    
    print(f"\n多轨道计算结果:")
    for orbital, result in multi_results.items():
        print(f"  {orbital:6s}: 相关系数={result['correlation']:.4f}, "
              f"耗时={result['time']:.2f}s, 剩余点数={result['final_points']}")
    
    avg_correlation = np.mean([r['correlation'] for r in multi_results.values()])
    avg_time = np.mean([r['time'] for r in multi_results.values()])
    
    print(f"\n平均性能:")
    print(f"  平均相关系数: {avg_correlation:.4f}")
    print(f"  平均计算时间: {avg_time:.2f} 秒")
    
    print(f"\n算法特点:")
    print(f"  ✓ 物理直观的累积-衰减机制")
    print(f"  ✓ 数值稳定，自然收敛")
    print(f"  ✓ 支持多种轨道类型")
    print(f"  ✓ 可视化功能丰富")
    print(f"  ✓ 高级优化功能完备")
    
    print("\n演示完成！所有结果已保存到当前目录")

def main():
    """主演示函数"""
    print("🚀 电子云轨道计算器完整演示")
    print("基于累积-衰减机制的创新量子轨道计算方法")
    print("="*60)
    
    # 确保输出目录存在
    os.makedirs('电子云轨道计算', exist_ok=True)
    
    # 1. 基础计算演示
    calc, basic_correlation = demo_basic_calculation()
    
    # 2. 多轨道计算演示
    multi_results = demo_multiple_orbitals()
    
    # 3. 收敛性分析
    convergence_data = demo_convergence_analysis()
    
    # 4. 高级功能演示
    advanced_solver = demo_advanced_features()
    
    # 5. 保存数据到Excel
    save_demo_data_to_excel(basic_correlation, multi_results, advanced_solver, convergence_data)
    
    # 6. 生成总结报告
    create_summary_report(basic_correlation, multi_results, advanced_solver)
    
    print(f"\n🎉 演示完成！")
    print(f"📁 图表文件已保存到: 电子云轨道计算/")
    print(f"📊 Excel数据已保存到: demo_results.xlsx")
    print(f"📈 查看 demo_summary_report.png 获取完整总结")

if __name__ == "__main__":
    main()