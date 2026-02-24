import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体显示
rcParams['font.family'] = 'SimHei'  # 使用黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def replace_negative_with_zero(matrix):
    # 使用 NumPy 数组操作，将小于 0 的元素替换为 0
    matrix[matrix < 0] = 0
    return matrix

# 参数定义
Lx, Ly = 1.0, 1.0  # 各个方向上的长度
num_points = 500   # 每个方向上的分割数

# 能级及其对应的概率
energy_levels = [(2, 1), (2, 1)]
probabilities = [0.5, 0.5]  # 各能级占据概率

# 定义普朗克常数和粒子质量（单位设置为适合计算）
hbar = 1.0545718e-34
m = 9.10938356e-31

# x 和 y 坐标
x = np.linspace(0, Lx, num_points)
y = np.linspace(0, Ly, num_points)
X, Y = np.meshgrid(x, y)

# 初始化总概率密度
total_prob_density = np.zeros_like(X)

# 计算每个能级的概率密度并加权求和
for (nx, ny), prob in zip(energy_levels, probabilities):
    psi_nx = np.sqrt(2 / Lx) * np.sin(nx * np.pi * X / Lx)
    psi_ny = np.sqrt(2 / Ly) * np.sin(ny * np.pi * Y / Ly)
    psi = psi_nx * psi_ny
    prob_density = psi**2
    total_prob_density += prob_density * prob

# 找到矩阵的最小值和最大值
C_min = total_prob_density.min()
C_max = total_prob_density.max()

# 进行归一化操作
C_normalized = (total_prob_density - C_min) / (C_max - C_min)
C_normalized -= 0.0
C_normalized[C_normalized < 0] = 0

# 打印矩阵
print("归一化概率密度矩阵：")
print(C_normalized)
print("矩阵最大值：", C_normalized.max())



# 按需启动二维部分
# 绘制二维概率密度分布的灰度图（概率越高，颜色越黑）
# plt.figure(figsize=(8, 6))
# plt.imshow(replace_negative_with_zero(C_normalized), 
#            cmap='gray_r', 
#            extent=[0, Lx, 0, Ly], 
#            origin='lower')
# plt.title('二维概率密度分布')  # 修改为中文标题
# plt.xlabel('X轴坐标')        # 修改为中文标签
# plt.ylabel('Y轴坐标')        # 修改为中文标签
# cbar = plt.colorbar()
# cbar.set_label('概率密度')   # 修改colorbar标签
# plt.show()


# 按需启动一维部分
# import matplotlib.pyplot as plt
# from matplotlib import rcParams


# rcParams['font.family'] = 'sans-serif' 
# rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC']  
# rcParams['axes.unicode_minus'] = False  

# # 绘制中间行数据的新图表
# mid_index = num_points // 2
# mid_row_data = C_normalized[mid_index, :]

# # 创建画布和坐标轴
# plt.figure(figsize=(10, 6))

# # 绘制中间行数据折线图（保持原有样式）
# plt.plot(x, mid_row_data, color='black', linewidth=1.5, linestyle='-', alpha=0.8)

# # 设置图表样式（中文字体已生效）
# plt.title(f'中心截线概率密度分布 (y = {y[mid_index]:.2f})')
# plt.xlabel('X坐标位置')
# plt.ylabel('归一化概率密度')
# plt.grid(True, linestyle='--', alpha=0.5)
# plt.xlim(0, Lx)
# plt.ylim(0, 1.1)


# plt.show()

# # 统计信息输出（保持原样）
# print("中间行统计结果：")
# print(f"最大值位置: x = {x[np.argmax(mid_row_data)]:.3f}")
# print(f"平均值: {np.mean(mid_row_data):.4f}")
# print(f"标准差: {np.std(mid_row_data):.4f}")

# 灰度图展示
# import matplotlib.pyplot as plt
# from matplotlib import rcParams
# import numpy as np

# # 中文字体配置（保持原设置）
# rcParams['font.family'] = 'sans-serif' 
# rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sa ns CJK SC']  
# rcParams['axes.unicode_minus'] = False  

# # 转换数据为二维灰度图格式
# mid_index = num_points // 2
# mid_row_data = C_normalized[mid_index, :]

# # 将一维数据转换为二维灰度图格式（添加高度维度）
# gray_data = np.expand_dims(mid_row_data, axis=0)  # 形状变为(1, num_points)

# # 创建画布和坐标轴
# plt.figure(figsize=(10, 2))  # 调整高度适应灰度图显示

# # 绘制灰度图（关键修改部分）
# im = plt.imshow(gray_data, 
#                 cmap='plasma_r', 
#                 aspect='auto',
#                 extent=[0, Lx, 0, 1],  # X轴范围与原始数据一致
#                 vmin=0, vmax=1)  # 明确设置数值范围[3,7](@ref)

# # 设置图表样式
# plt.title(f'中心截线概率密度分布 (y = {y[mid_index]:.2f})')
# plt.xlabel('X坐标位置')
# plt.ylabel('')  # 隐藏Y轴标签
# plt.yticks([])  # 移除Y轴刻度
# plt.grid(False)  # 关闭网格
# plt.xlim(0, Lx)

# # 添加颜色条
# cbar = plt.colorbar(im, shrink=0.8)
# cbar.set_label('归一化概率密度')

# plt.show()

# # 统计信息输出（保持原样）
# print("中间行统计结果：")
# print(f"最大值位置: x = {x[np.argmax(mid_row_data)]:.3f}")
# print(f"平均值: {np.mean(mid_row_data):.4f}")
# print(f"标准差: {np.std(mid_row_data):.4f}")


