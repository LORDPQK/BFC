#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子云轨道计算器 - 基于累积衰减机制
使用三维空间矩阵的累积-衰减算法来计算电子云轨道分布
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.special as sp
from scipy.optimize import minimize_scalar
import time

class OrbitalCalculator:
    """电子云轨道计算器"""
    
    def __init__(self, grid_size=100, space_range=10.0):
        """
        初始化计算器
        :param grid_size: 网格大小 (每个维度的点数)
        :param space_range: 空间范围 (-space_range 到 +space_range)
        """
        self.grid_size = grid_size
        self.space_range = space_range
        
        # 创建三维网格
        self.x = np.linspace(-space_range, space_range, grid_size)
        self.y = np.linspace(-space_range, space_range, grid_size)
        self.z = np.linspace(-space_range, space_range, grid_size)
        self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')
        
        # 计算球坐标
        self.r = np.sqrt(self.X**2 + self.Y**2 + self.Z**2)
        self.theta = np.arccos(np.divide(self.Z, self.r, out=np.zeros_like(self.Z), where=self.r!=0))
        self.phi = np.arctan2(self.Y, self.X)
        
        # 初始化累积矩阵
        self.accumulation_matrix = np.zeros((grid_size, grid_size, grid_size))
        
        # 物理常数 (原子单位)
        self.bohr_radius = 1.0  # 玻尔半径
        
    def hydrogen_wavefunction(self, n, l, m):
        """
        计算氢原子波函数的理论值
        :param n: 主量子数
        :param l: 角量子数  
        :param m: 磁量子数
        :return: 波函数值矩阵
        """
        # 径向部分
        rho = 2 * self.r / (n * self.bohr_radius)
        
        # 拉盖尔多项式系数
        L_coeff = sp.genlaguerre(n-l-1, 2*l+1)
        
        # 径向波函数
        R_nl = np.sqrt((2/(n*self.bohr_radius))**3 * 
                      sp.factorial(n-l-1)/(2*n*sp.factorial(n+l))) * \
               np.exp(-rho/2) * (rho**l) * L_coeff(rho)
        
        # 球谐函数
        Y_lm = sp.sph_harm(m, l, self.phi, self.theta)
        
        # 完整波函数
        psi = R_nl * Y_lm
        
        return psi
    
    def add_initial_wavefunction(self, n, l, m, strength=1.0):
        """
        在累积矩阵中添加初始波函数
        :param n: 主量子数
        :param l: 角量子数
        :param m: 磁量子数  
        :param strength: 添加强度
        """
        psi = self.hydrogen_wavefunction(n, l, m)
        
        # 计算概率密度
        probability_density = np.abs(psi)**2
        
        # 添加到累积矩阵
        self.accumulation_matrix += strength * probability_density
        
        print(f"已添加 n={n}, l={l}, m={m} 轨道，强度={strength}")
    
    def apply_decay(self, decay_rate=0.95, threshold=1e-6):
        """
        对累积矩阵应用衰减
        :param decay_rate: 衰减率 (0-1之间)
        :param threshold: 阈值，低于此值的点被清零
        """
        # 应用衰减
        self.accumulation_matrix *= decay_rate
        
        # 应用阈值
        self.accumulation_matrix[self.accumulation_matrix < threshold] = 0
        
        # 返回剩余的非零点数量
        return np.count_nonzero(self.accumulation_matrix)
    
    def iterative_solve(self, n, l, m, iterations=1000, 
                       add_strength=1.0, decay_rate=0.98, 
                       add_frequency=10):
        """
        迭代求解电子云轨道
        :param n: 主量子数
        :param l: 角量子数
        :param m: 磁量子数
        :param iterations: 迭代次数
        :param add_strength: 每次添加的强度
        :param decay_rate: 衰减率
        :param add_frequency: 添加频率 (每多少次迭代添加一次)
        """
        print(f"开始迭代求解 n={n}, l={l}, m={m} 轨道...")
        
        # 重置累积矩阵
        self.accumulation_matrix = np.zeros_like(self.accumulation_matrix)
        
        # 记录收敛历史
        convergence_history = []
        
        for i in range(iterations):
            # 定期添加波函数
            if i % add_frequency == 0:
                self.add_initial_wavefunction(n, l, m, add_strength)
            
            # 应用衰减
            remaining_points = self.apply_decay(decay_rate)
            
            # 记录收敛情况
            max_value = np.max(self.accumulation_matrix)
            convergence_history.append((i, remaining_points, max_value))
            
            # 打印进度
            if i % 100 == 0:
                print(f"迭代 {i}: 剩余点数={remaining_points}, 最大值={max_value:.6f}")
        
        print(f"迭代完成！最终剩余点数: {remaining_points}")
        return convergence_history
    
    def visualize_orbital(self, slice_type='xy', slice_position=0, 
                         title="电子云轨道分布"):
        """
        可视化电子云轨道
        :param slice_type: 切片类型 ('xy', 'xz', 'yz')
        :param slice_position: 切片位置索引
        :param title: 图表标题
        """
        plt.figure(figsize=(12, 10))
        
        if slice_type == 'xy':
            slice_data = self.accumulation_matrix[:, :, slice_position]
            extent = [-self.space_range, self.space_range, 
                     -self.space_range, self.space_range]
            plt.xlabel('X (玻尔半径)')
            plt.ylabel('Y (玻尔半径)')
            
        elif slice_type == 'xz':
            slice_data = self.accumulation_matrix[:, slice_position, :]
            extent = [-self.space_range, self.space_range, 
                     -self.space_range, self.space_range]
            plt.xlabel('X (玻尔半径)')
            plt.ylabel('Z (玻尔半径)')
            
        elif slice_type == 'yz':
            slice_data = self.accumulation_matrix[slice_position, :, :]
            extent = [-self.space_range, self.space_range, 
                     -self.space_range, self.space_range]
            plt.xlabel('Y (玻尔半径)')
            plt.ylabel('Z (玻尔半径)')
        
        # 绘制热力图
        im = plt.imshow(slice_data.T, extent=extent, origin='lower', 
                       cmap='hot', interpolation='bilinear')
        plt.colorbar(im, label='电子云密度')
        plt.title(f'{title} - {slice_type.upper()}切片')
        plt.grid(True, alpha=0.3)
        
        return plt.gcf()
    
    def visualize_3d_orbital(self, threshold_percentile=90, alpha=0.3):
        """
        3D可视化电子云轨道
        :param threshold_percentile: 显示阈值百分位数
        :param alpha: 透明度
        """
        # 计算阈值
        threshold = np.percentile(self.accumulation_matrix[self.accumulation_matrix > 0], 
                                threshold_percentile)
        
        # 找到高密度区域
        high_density = self.accumulation_matrix > threshold
        
        # 获取坐标
        x_coords = self.X[high_density]
        y_coords = self.Y[high_density]
        z_coords = self.Z[high_density]
        values = self.accumulation_matrix[high_density]
        
        # 创建3D图
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制散点图
        scatter = ax.scatter(x_coords, y_coords, z_coords, 
                           c=values, cmap='hot', alpha=alpha, s=1)
        
        ax.set_xlabel('X (玻尔半径)')
        ax.set_ylabel('Y (玻尔半径)')
        ax.set_zlabel('Z (玻尔半径)')
        ax.set_title('电子云轨道 3D 分布')
        
        plt.colorbar(scatter, label='电子云密度')
        
        return fig
    
    def compare_with_theory(self, n, l, m):
        """
        与理论波函数比较
        :param n: 主量子数
        :param l: 角量子数
        :param m: 磁量子数
        """
        # 计算理论波函数
        theoretical_psi = self.hydrogen_wavefunction(n, l, m)
        theoretical_density = np.abs(theoretical_psi)**2
        
        # 归一化两个分布以便比较
        theory_normalized = theoretical_density / np.max(theoretical_density)
        computed_normalized = self.accumulation_matrix / np.max(self.accumulation_matrix)
        
        # 计算相关系数
        mask = (theory_normalized > 1e-6) & (computed_normalized > 1e-6)
        if np.sum(mask) > 0:
            correlation = np.corrcoef(theory_normalized[mask].flatten(), 
                                    computed_normalized[mask].flatten())[0, 1]
        else:
            correlation = 0
        
        print(f"与理论值的相关系数: {correlation:.4f}")
        
        # 可视化比较
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # 中间切片
        mid_slice = self.grid_size // 2
        
        # 理论值
        axes[0].imshow(theory_normalized[:, :, mid_slice].T, 
                      extent=[-self.space_range, self.space_range, 
                             -self.space_range, self.space_range],
                      origin='lower', cmap='hot')
        axes[0].set_title('理论波函数密度')
        axes[0].set_xlabel('X (玻尔半径)')
        axes[0].set_ylabel('Y (玻尔半径)')
        
        # 计算结果
        axes[1].imshow(computed_normalized[:, :, mid_slice].T,
                      extent=[-self.space_range, self.space_range, 
                             -self.space_range, self.space_range],
                      origin='lower', cmap='hot')
        axes[1].set_title('累积-衰减算法结果')
        axes[1].set_xlabel('X (玻尔半径)')
        axes[1].set_ylabel('Y (玻尔半径)')
        
        # 差异
        difference = np.abs(theory_normalized - computed_normalized)
        im = axes[2].imshow(difference[:, :, mid_slice].T,
                           extent=[-self.space_range, self.space_range, 
                                  -self.space_range, self.space_range],
                           origin='lower', cmap='viridis')
        axes[2].set_title('差异分布')
        axes[2].set_xlabel('X (玻尔半径)')
        axes[2].set_ylabel('Y (玻尔半径)')
        
        plt.tight_layout()
        return fig, correlation


def main():
    """主函数 - 演示电子云轨道计算"""
    print("=== 电子云轨道计算器演示 ===")
    
    # 创建计算器实例
    calculator = OrbitalCalculator(grid_size=80, space_range=8.0)
    
    # 测试不同的轨道
    orbitals_to_test = [
        (1, 0, 0),  # 1s轨道
        (2, 0, 0),  # 2s轨道
        (2, 1, 0),  # 2p轨道
        (2, 1, 1),  # 2p轨道
    ]
    
    for n, l, m in orbitals_to_test:
        print(f"\n--- 计算 n={n}, l={l}, m={m} 轨道 ---")
        
        # 迭代求解
        start_time = time.time()
        history = calculator.iterative_solve(n, l, m, 
                                           iterations=500,
                                           add_strength=0.1,
                                           decay_rate=0.99,
                                           add_frequency=5)
        end_time = time.time()
        
        print(f"计算耗时: {end_time - start_time:.2f} 秒")
        
        # 保存可视化结果
        fig1 = calculator.visualize_orbital('xy', calculator.grid_size//2, 
                                          f"n={n}_l={l}_m={m}_轨道")
        plt.savefig(f'电子云轨道计算/orbital_n{n}_l{l}_m{m}_xy.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3D可视化
        fig2 = calculator.visualize_3d_orbital(threshold_percentile=85)
        plt.savefig(f'电子云轨道计算/orbital_n{n}_l{l}_m{m}_3d.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 与理论比较
        fig3, correlation = calculator.compare_with_theory(n, l, m)
        plt.savefig(f'电子云轨道计算/comparison_n{n}_l{l}_m{m}.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"结果已保存，相关系数: {correlation:.4f}")


if __name__ == "__main__":
    main()