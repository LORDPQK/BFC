#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt

def test_basic_functionality():
    """测试基础功能"""
    print("=== 基础功能测试 ===")
    
    try:
        from orbital_calculator import OrbitalCalculator
        print("✓ 基础计算器导入成功")
    except Exception as e:
        print(f"✗ 基础计算器导入失败: {e}")
        return False
    
    try:
        from advanced_orbital_solver import AdvancedOrbitalSolver
        print("✓ 高级求解器导入成功")
    except Exception as e:
        print(f"✗ 高级求解器导入失败: {e}")
        return False
    
    # 创建小规模测试实例
    try:
        calc = OrbitalCalculator(grid_size=20, space_range=3.0)
        print("✓ 基础计算器创建成功")
        
        # 测试波函数计算
        psi = calc.hydrogen_wavefunction(1, 0, 0)
        print(f"✓ 1s波函数计算成功，形状: {psi.shape}")
        print(f"  最大值: {np.max(np.abs(psi)):.6f}")
        
        # 测试累积矩阵初始化
        print(f"✓ 累积矩阵形状: {calc.accumulation_matrix.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_small_calculation():
    """测试小规模计算"""
    print("\n=== 小规模计算测试 ===")
    
    try:
        from orbital_calculator import OrbitalCalculator
        
        # 创建很小的网格进行快速测试
        calc = OrbitalCalculator(grid_size=15, space_range=2.0)
        
        # 进行少量迭代
        print("开始小规模1s轨道计算...")
        history = calc.iterative_solve(1, 0, 0, iterations=50, 
                                      add_strength=0.3, decay_rate=0.95, 
                                      add_frequency=2)
        
        print(f"✓ 计算完成，迭代历史长度: {len(history)}")
        
        if history:
            final_points = history[-1][1]
            final_max = history[-1][2]
            print(f"  最终剩余点数: {final_points}")
            print(f"  最终最大值: {final_max:.6f}")
        
        # 测试可视化（不显示）
        fig = calc.visualize_orbital('xy', calc.grid_size//2, "测试1s轨道")
        plt.savefig('test_1s_small.png', dpi=100, bbox_inches='tight')
        plt.close()
        print("✓ 可视化测试成功，图像已保存")
        
        return True
        
    except Exception as e:
        print(f"✗ 小规模计算失败: {e}")
        return False

def test_advanced_solver():
    """测试高级求解器"""
    print("\n=== 高级求解器测试 ===")
    
    try:
        from advanced_orbital_solver import AdvancedOrbitalSolver
        
        # 创建高级求解器
        solver = AdvancedOrbitalSolver(grid_size=15, space_range=2.0, 
                                      adaptive_grid=False, energy_minimization=False)
        print("✓ 高级求解器创建成功")
        
        # 测试波函数计算
        psi = solver.hydrogen_wavefunction_exact(1, 0, 0)
        print(f"✓ 精确波函数计算成功，形状: {psi.shape}")
        
        # 测试多轨道叠加
        orbital_configs = [(1, 0, 0)]
        weights = [1.0]
        solver.multi_orbital_superposition(orbital_configs, weights)
        print("✓ 多轨道叠加测试成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 高级求解器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始电子云轨道计算器测试...\n")
    
    results = []
    
    # 基础功能测试
    results.append(test_basic_functionality())
    
    # 小规模计算测试
    results.append(test_small_calculation())
    
    # 高级求解器测试
    results.append(test_advanced_solver())
    
    # 总结
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"测试总结: {passed}/{total} 项测试通过")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 所有测试通过！电子云轨道计算器工作正常。")
    else:
        print("⚠️  部分测试失败，请检查依赖库安装。")
    
    return passed == total

if __name__ == "__main__":
    main()