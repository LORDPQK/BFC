#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子云轨道计算测试脚本
快速验证累积-衰减算法的有效性
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from orbital_calculator import OrbitalCalculator
from advanced_orbital_solver import AdvancedOrbitalSolver

def quick_test():
    """快速测试基本功能"""
    print("=== 快速测试 ===")
    
    # 创建基础计算器
    calc = OrbitalCalculator(grid_size=50, space_range=6.0)
    
    # 测试1s轨道
    print("测试1s轨道...")
    start_time = time.time()
    
    history = calc.iterative_solve(1, 0, 0, iterations=300, 
                                  add_strength=0.2, decay_rate=0.98, 
                                  add_frequency=3)
    
    end_time = time.time()
    print(f"计算耗时: {end_time - start_time:.2f} 秒")
    
    # 可视化结果
    fig = calc.visualize_orbital('xy', calc.grid_size//2, "1s轨道测试")
    plt.savefig('电子云轨道计算/test_1s_orbital.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # 与理论比较
    fig, correlation = calc.compare_with_theory(1, 0, 0)
    plt.savefig('电子云轨道计算/test_1s_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"1s轨道相关系数: {correlation:.4f}")
    
    return correlation > 0.8  # 如果相关系数大于0.8认为测试通过

def parameter_optimization_test():
    """参数优化测试"""
    print("\n=== 参数优化测试 ===")
    
    calc = OrbitalCalculator(grid_size=40, space_range=5.0)
    
    # 测试不同参数组合
    param_sets = [
        {'decay_rate': 0.95, 'add_strength': 0.1, 'add_frequency': 5},
        {'decay_rate': 0.98, 'add_strength': 0.2, 'add_frequency': 3},
        {'decay_rate': 0.99, 'add_strength': 0.05, 'add_frequency': 8},
    ]
    
    best_correlation = 0
    best_params = None
    
    for i, params in enumerate(param_sets):
        print(f"测试参数组合 {i+1}: {params}")
        
        history = calc.iterative_solve(1, 0, 0, iterations=200, **params)
        fig, correlation = calc.compare_with_theory(1, 0, 0)
        plt.close()  # 不显示图像
        
        print(f"相关系数: {correlation:.4f}")
        
        if correlation > best_correlation:
            best_correlation = correlation
            best_params = params
    
    print(f"最佳参数: {best_params}")
    print(f"最佳相关系数: {best_correlation:.4f}")
    
    return best_params

def advanced_solver_test():
    """高级求解器测试"""
    print("\n=== 高级求解器测试 ===")
    
    # 创建高级求解器
    solver = AdvancedOrbitalSolver(grid_size=40, space_range=6.0, 
                                  adaptive_grid=True, energy_minimization=True)
    
    # 测试2p轨道
    print("测试2p轨道...")
    start_time = time.time()
    
    convergence_hist, energy_hist = solver.solve_with_optimization(2, 1, 0, max_iterations=400)
    
    end_time = time.time()
    print(f"高级求解耗时: {end_time - start_time:.2f} 秒")
    
    # 可视化
    fig = solver.advanced_visualization(2, 1, 0, '电子云轨道计算/test_advanced_2p.png')
    plt.show()
    
    # 检查能量收敛
    if energy_hist:
        final_energy = energy_hist[-1][1]
        theoretical_energy = -1.0 / (2 * 2**2)  # 氢原子2p轨道理论能量
        energy_error = abs(final_energy - theoretical_energy) / abs(theoretical_energy)
        print(f"计算能量: {final_energy:.6f}")
        print(f"理论能量: {theoretical_energy:.6f}")
        print(f"相对误差: {energy_error:.2%}")
        
        return energy_error < 0.1  # 如果误差小于10%认为测试通过
    
    return True

def convergence_analysis():
    """收敛性分析"""
    print("\n=== 收敛性分析 ===")
    
    calc = OrbitalCalculator(grid_size=40, space_range=5.0)
    
    # 测试不同迭代次数的收敛情况
    iteration_counts = [100, 200, 400, 800]
    correlations = []
    
    for iterations in iteration_counts:
        print(f"测试 {iterations} 次迭代...")
        
        history = calc.iterative_solve(1, 0, 0, iterations=iterations,
                                      add_strength=0.15, decay_rate=0.98, 
                                      add_frequency=4)
        
        fig, correlation = calc.compare_with_theory(1, 0, 0)
        plt.close()
        
        correlations.append(correlation)
        print(f"相关系数: {correlation:.4f}")
    
    # 绘制收敛曲线
    plt.figure(figsize=(10, 6))
    plt.plot(iteration_counts, correlations, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('迭代次数')
    plt.ylabel('与理论值的相关系数')
    plt.title('算法收敛性分析')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    
    # 添加收敛阈值线
    plt.axhline(y=0.9, color='r', linestyle='--', alpha=0.7, label='目标阈值 (0.9)')
    plt.legend()
    
    plt.savefig('电子云轨道计算/convergence_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return correlations

def multi_orbital_test():
    """多轨道测试"""
    print("\n=== 多轨道测试 ===")
    
    calc = OrbitalCalculator(grid_size=35, space_range=5.0)
    
    # 测试不同轨道
    orbitals = [(1, 0, 0), (2, 0, 0), (2, 1, 0), (2, 1, 1)]
    results = {}
    
    for n, l, m in orbitals:
        print(f"测试 n={n}, l={l}, m={m} 轨道...")
        
        start_time = time.time()
        history = calc.iterative_solve(n, l, m, iterations=300,
                                      add_strength=0.15, decay_rate=0.98,
                                      add_frequency=4)
        end_time = time.time()
        
        fig, correlation = calc.compare_with_theory(n, l, m)
        plt.close()
        
        results[(n, l, m)] = {
            'correlation': correlation,
            'time': end_time - start_time,
            'final_points': history[-1][1] if history else 0
        }
        
        print(f"相关系数: {correlation:.4f}, 耗时: {end_time - start_time:.2f}秒")
    
    # 总结结果
    print("\n=== 多轨道测试总结 ===")
    for orbital, result in results.items():
        n, l, m = orbital
        print(f"n={n}, l={l}, m={m}: 相关系数={result['correlation']:.4f}, "
              f"耗时={result['time']:.2f}秒, 剩余点数={result['final_points']}")
    
    return results

def main():
    """主测试函数"""
    print("开始电子云轨道计算测试...")
    
    # 创建输出目录
    import os
    os.makedirs('电子云轨道计算', exist_ok=True)
    
    test_results = {}
    
    # 1. 快速测试
    try:
        test_results['quick_test'] = quick_test()
        print(f"快速测试: {'通过' if test_results['quick_test'] else '失败'}")
    except Exception as e:
        print(f"快速测试失败: {e}")
        test_results['quick_test'] = False
    
    # 2. 参数优化测试
    try:
        test_results['best_params'] = parameter_optimization_test()
        print("参数优化测试: 完成")
    except Exception as e:
        print(f"参数优化测试失败: {e}")
        test_results['best_params'] = None
    
    # 3. 高级求解器测试
    try:
        test_results['advanced_test'] = advanced_solver_test()
        print(f"高级求解器测试: {'通过' if test_results['advanced_test'] else '失败'}")
    except Exception as e:
        print(f"高级求解器测试失败: {e}")
        test_results['advanced_test'] = False
    
    # 4. 收敛性分析
    try:
        test_results['convergence'] = convergence_analysis()
        print("收敛性分析: 完成")
    except Exception as e:
        print(f"收敛性分析失败: {e}")
        test_results['convergence'] = None
    
    # 5. 多轨道测试
    try:
        test_results['multi_orbital'] = multi_orbital_test()
        print("多轨道测试: 完成")
    except Exception as e:
        print(f"多轨道测试失败: {e}")
        test_results['multi_orbital'] = None
    
    # 总结
    print("\n" + "="*50)
    print("测试总结:")
    print("="*50)
    
    passed_tests = sum([1 for k, v in test_results.items() 
                       if k in ['quick_test', 'advanced_test'] and v])
    total_tests = 2
    
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if test_results.get('best_params'):
        print(f"推荐参数: {test_results['best_params']}")
    
    if test_results.get('convergence'):
        max_correlation = max(test_results['convergence'])
        print(f"最高相关系数: {max_correlation:.4f}")
    
    print("\n算法验证完成！")
    
    return test_results

if __name__ == "__main__":
    main()