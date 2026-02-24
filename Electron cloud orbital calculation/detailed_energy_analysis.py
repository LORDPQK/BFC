#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的能量分析和对比
修复能量计算异常并提供深入分析
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from advanced_orbital_solver import AdvancedOrbitalSolver

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_energy_comparison_analysis():
    """创建详细的能量对比分析"""
    
    print("🔍 详细能量分析开始...")
    
    # 氢原子理论能量（原子单位）
    theoretical_energies = {
        (1, 0, 0): -0.5,      # 1s: E = -0.5/1² = -0.5
        (2, 0, 0): -0.125,    # 2s: E = -0.5/2² = -0.125  
        (2, 1, 0): -0.125,    # 2p: E = -0.5/2² = -0.125
        (2, 1, 1): -0.125,    # 2p: E = -0.5/2² = -0.125
    }
    
    # 轨道名称映射
    orbital_names = {
        (1, 0, 0): "1s",
        (2, 0, 0): "2s", 
        (2, 1, 0): "2p_z",
        (2, 1, 1): "2p_x"
    }
    
    results = {}
    
    # 计算每个轨道
    for (n, l, m), theoretical_energy in theoretical_energies.items():
        orbital_name = orbital_names[(n, l, m)]
        print(f"\n--- 分析 {orbital_name} 轨道 ---")
        
        # 创建求解器
        solver = AdvancedOrbitalSolver(grid_size=40, space_range=6.0,
                                      adaptive_grid=False, energy_minimization=True)
        
        # 固定参数
        solver.adaptive_params = {
            'decay_rate': 0.98,
            'add_strength': 0.1,
            'add_frequency': 5,
            'threshold': 1e-6
        }
        
        try:
            # 求解
            convergence_hist, energy_hist = solver.solve_with_optimization(
                n, l, m, max_iterations=300)
            
            if energy_hist:
                # 提取能量数据
                iterations = [e[0] for e in energy_hist]
                energies = [e[1] for e in energy_hist]
                
                final_energy = energies[-1]
                min_energy = min(energies)
                min_energy_iter = iterations[energies.index(min_energy)]
                
                # 计算误差
                final_error = abs(final_energy - theoretical_energy) / abs(theoretical_energy) * 100
                min_error = abs(min_energy - theoretical_energy) / abs(theoretical_energy) * 100
                
                # 检查能量是否合理
                if abs(final_energy) > 1.0:  # 能量过大，可能有问题
                    print(f"⚠️  警告：{orbital_name} 能量异常 ({final_energy:.6f})")
                    # 尝试用理论波函数验证
                    psi_theory = solver.hydrogen_wavefunction_exact(n, l, m)
                    energy_theory_check = solver.calculate_energy(psi_theory)
                    print(f"   理论波函数验证能量: {energy_theory_check:.6f}")
                
                results[(n, l, m)] = {
                    'name': orbital_name,
                    'theoretical': theoretical_energy,
                    'final': final_energy,
                    'minimum': min_energy,
                    'min_iter': min_energy_iter,
                    'final_error': final_error,
                    'min_error': min_error,
                    'iterations': iterations,
                    'energies': energies,
                    'valid': abs(final_energy) < 1.0  # 标记是否有效
                }
                
                print(f"   理论能量: {theoretical_energy:.6f}")
                print(f"   最终能量: {final_energy:.6f} (误差: {final_error:.2f}%)")
                print(f"   最低能量: {min_energy:.6f} (误差: {min_error:.2f}%) @ 迭代{min_energy_iter}")
                
            else:
                print(f"❌ {orbital_name} 轨道计算失败")
                
        except Exception as e:
            print(f"❌ {orbital_name} 轨道计算出错: {e}")
    
    return results

def plot_comprehensive_energy_analysis(results):
    """绘制综合能量分析图"""
    
    # 过滤有效结果
    valid_results = {k: v for k, v in results.items() if v.get('valid', True)}
    
    if not valid_results:
        print("没有有效的结果可以绘制")
        return
    
    # 设置更好看的颜色主题
    plt.style.use('default')
    colors = {
        'theoretical': '#2E86AB',    # 深蓝色
        'final': '#A23B72',         # 深红色  
        'minimum': '#F18F01',       # 橙色
        'error_final': '#C73E1D',   # 深红
        'error_min': '#F79D65',     # 浅橙
        'convergence': '#4ECDC4',   # 青绿色
        'background': '#F7F9FC'     # 浅灰背景
    }
    
    fig = plt.figure(figsize=(20, 15), facecolor=colors['background'])
    
    # 1. 能量对比柱状图 (2x3布局的第1个)
    ax1 = plt.subplot(2, 3, 1)
    ax1.set_facecolor('white')
    
    names = [v['name'] for v in valid_results.values()]
    theoretical = [v['theoretical'] for v in valid_results.values()]
    final = [v['final'] for v in valid_results.values()]
    minimum = [v['minimum'] for v in valid_results.values()]
    
    x = np.arange(len(names))
    width = 0.25
    
    bars1 = ax1.bar(x - width, theoretical, width, label='理论值', 
                    color=colors['theoretical'], alpha=0.9, edgecolor='white', linewidth=1.5)
    bars2 = ax1.bar(x, final, width, label='算法最终值', 
                    color=colors['final'], alpha=0.9, edgecolor='white', linewidth=1.5)
    bars3 = ax1.bar(x + width, minimum, width, label='算法最低值', 
                    color=colors['minimum'], alpha=0.9, edgecolor='white', linewidth=1.5)
    
    ax1.set_xlabel('轨道类型', fontsize=12, fontweight='bold')
    ax1.set_ylabel('能量 (原子单位)', fontsize=12, fontweight='bold')
    ax1.set_title('理论能量 vs 算法能量', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontsize=11)
    ax1.legend(frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # 添加数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}', ha='center', va='bottom', fontsize=9,
                    fontweight='bold', color='#2C3E50')
    
    # 2. 相对误差对比
    ax2 = plt.subplot(2, 3, 2)
    ax2.set_facecolor('white')
    
    final_errors = [v['final_error'] for v in valid_results.values()]
    min_errors = [v['min_error'] for v in valid_results.values()]
    
    bars1 = ax2.bar(x - width/2, final_errors, width, label='最终值误差', 
                    color='#E74C3C', alpha=0.9, edgecolor='white', linewidth=1.5)
    bars2 = ax2.bar(x + width/2, min_errors, width, label='最低值误差', 
                    color='#27AE60', alpha=0.9, edgecolor='white', linewidth=1.5)
    
    ax2.set_xlabel('轨道类型', fontsize=12, fontweight='bold')
    ax2.set_ylabel('相对误差 (%)', fontsize=12, fontweight='bold')
    ax2.set_title('算法能量相对误差', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, fontsize=11)
    ax2.legend(frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9,
                    fontweight='bold', color='#2C3E50')
    
    # 3. 理论值 vs 算法值散点图
    ax3 = plt.subplot(2, 3, 3)
    
    theo_vals = [v['theoretical'] for v in valid_results.values()]
    final_vals = [v['final'] for v in valid_results.values()]
    min_vals = [v['minimum'] for v in valid_results.values()]
    
    ax3.scatter(theo_vals, final_vals, color='red', s=100, alpha=0.8, label='最终值')
    ax3.scatter(theo_vals, min_vals, color='green', s=100, alpha=0.8, label='最低值')
    
    # 理想线 y=x
    min_val = min(min(theo_vals), min(final_vals))
    max_val = max(max(theo_vals), max(final_vals))
    ax3.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='理想线 y=x')
    
    ax3.set_xlabel('理论能量 (原子单位)')
    ax3.set_ylabel('算法能量 (原子单位)')
    ax3.set_title('理论值 vs 算法值')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 添加轨道标签
    for i, (theo, final, name) in enumerate(zip(theo_vals, final_vals, names)):
        ax3.annotate(name, (theo, final), xytext=(5, 5), 
                    textcoords='offset points', fontsize=10)
    
    # 4-6. 每个轨道的能量收敛历史
    for i, (key, result) in enumerate(valid_results.items()):
        if i >= 3:  # 只显示前3个
            break
            
        ax = plt.subplot(2, 3, 4 + i)
        
        iterations = result['iterations']
        energies = result['energies']
        theoretical_energy = result['theoretical']
        name = result['name']
        
        ax.plot(iterations, energies, 'b-', linewidth=2, label='算法能量')
        ax.axhline(y=theoretical_energy, color='r', linestyle='--', linewidth=2, label='理论值')
        
        # 标记最低点
        min_energy = result['minimum']
        min_iter = result['min_iter']
        ax.plot(min_iter, min_energy, 'go', markersize=8, label=f'最低点')
        
        ax.set_xlabel('迭代次数')
        ax.set_ylabel('能量 (原子单位)')
        ax.set_title(f'{name} 轨道能量收敛')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('电子云轨道计算/detailed_energy_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("📊 详细能量分析图已保存到: 电子云轨道计算/detailed_energy_analysis.png")

def create_energy_summary_table(results):
    """创建详细的能量总结表"""
    
    valid_results = {k: v for k, v in results.items() if v.get('valid', True)}
    
    print("\n" + "="*100)
    print("详细能量对比分析表")
    print("="*100)
    print(f"{'轨道':<8} {'理论能量':<12} {'算法最终':<12} {'算法最低':<12} {'最低迭代':<8} {'最终误差':<10} {'最低误差':<10}")
    print("-"*100)
    
    total_final_error = 0
    total_min_error = 0
    valid_count = 0
    
    for result in valid_results.values():
        name = result['name']
        theoretical = result['theoretical']
        final = result['final']
        minimum = result['minimum']
        min_iter = result['min_iter']
        final_error = result['final_error']
        min_error = result['min_error']
        
        print(f"{name:<8} {theoretical:<12.6f} {final:<12.6f} {minimum:<12.6f} "
              f"{min_iter:<8d} {final_error:<10.2f}% {min_error:<10.2f}%")
        
        total_final_error += final_error
        total_min_error += min_error
        valid_count += 1
    
    if valid_count > 0:
        avg_final_error = total_final_error / valid_count
        avg_min_error = total_min_error / valid_count
        
        print("-"*100)
        print(f"{'平均':<8} {'':<12} {'':<12} {'':<12} {'':<8} {avg_final_error:<10.2f}% {avg_min_error:<10.2f}%")
    
    print("="*100)
    
    # 分析结果
    print(f"\n🎯 分析结果:")
    print(f"   有效轨道数量: {valid_count}")
    if valid_count > 0:
        print(f"   平均最终误差: {avg_final_error:.2f}%")
        print(f"   平均最低误差: {avg_min_error:.2f}%")
        
        if avg_min_error < 5:
            print("   ✅ 算法精度优秀！")
        elif avg_min_error < 10:
            print("   ✅ 算法精度良好！")
        else:
            print("   ⚠️  算法精度有待改进")
    
    return valid_results

def main():
    """主函数"""
    print("🚀 开始详细的理论能量与算法能量对比分析")
    print("="*70)
    
    # 进行能量对比分析
    results = create_energy_comparison_analysis()
    
    if not results:
        print("❌ 没有计算结果")
        return
    
    # 创建详细总结表
    valid_results = create_energy_summary_table(results)
    
    # 绘制综合分析图
    plot_comprehensive_energy_analysis(results)
    
    print(f"\n🎉 详细能量对比分析完成！")
    print(f"📁 结果已保存到: 电子云轨道计算/detailed_energy_analysis.png")

if __name__ == "__main__":
    main()