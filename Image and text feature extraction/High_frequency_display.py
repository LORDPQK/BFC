import cv2
import numpy as np
import pywt
import matplotlib.pyplot as plt

def adaptive_frequency_decay(image_path, decay_rate=1, high_freq_boost=1, wavelet='haar', timestamp=0):
    """自适应高频保留的图像衰减处理（修复尺寸不匹配问题）"""
    # 1. 读取图像并转为浮点型
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"图像 {image_path} 不存在")
    h, w = img.shape[:2]
    img_float = img.astype(np.float32) / 255.0

    # 2. 尺寸预处理：填充至偶数尺寸（小波变换要求）
    pad_h = (2 - h % 2) % 2  # 计算需要填充的高度
    pad_w = (2 - w % 2) % 2  # 计算需要填充的宽度
    img_padded = np.pad(img_float, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')

    # 3. 小波变换分离频段
    coeffs = pywt.dwt2(img_padded, wavelet, axes=(0, 1))
    LL, (LH, HL, HH) = coeffs

    # 4. 计算梯度图（使用灰度图避免通道不匹配）
    gray_img = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Scharr(gray_img, cv2.CV_32F, 1, 0)
    grad_y = cv2.Scharr(gray_img, cv2.CV_32F, 0, 1)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    
    # 5. 缩放梯度图到高频分量尺寸
    grad_mag_scaled = cv2.resize(grad_mag, (LH.shape[1], LH.shape[0]), interpolation=cv2.INTER_AREA)
    decay_map = np.clip(grad_mag_scaled * high_freq_boost, 0.8, 1.0)
    decay_map_3d = decay_map[..., np.newaxis]  # 形状 (LH_h, LH_w, 1)

    # 6. 时间衰减模型：高频抗衰减，低频快速衰减
    # 低频衰减：随时间指数衰减
    low_freq_decay = np.exp(-timestamp * 0.5)  # 低频快速衰减
    # 高频保持：基于梯度强度的抗衰减能力
    high_freq_resistance = decay_map_3d * np.exp(-timestamp * 0.1)  # 高频慢速衰减
    
    LL_decayed = LL * low_freq_decay * decay_rate
    LH_boosted = LH * high_freq_resistance * high_freq_boost
    HL_boosted = HL * high_freq_resistance * high_freq_boost
    HH_boosted = HH * high_freq_resistance * high_freq_boost

    # 7. 重组图像并裁剪回原始尺寸
    coeffs_decayed = (LL_decayed, (LH_boosted, HL_boosted, HH_boosted))
    img_decayed_padded = pywt.idwt2(coeffs_decayed, wavelet, axes=(0, 1))
    img_decayed = img_decayed_padded[:h, :w]  # 移除填充部分
    img_decayed = np.clip(img_decayed * 255, 0, 255).astype(np.uint8)
    

    # ===== 新增：提取并可视化衰减后剩余的高频特征 =====
    # 计算原始高频分量（未增强）
    original_high_freq = np.stack([LH, HL, HH])
    # 计算处理后的高频分量（已增强）
    processed_high_freq = np.stack([LH_boosted, HL_boosted, HH_boosted])
    
    # 高频特征可视化（取绝对值并归一化）
    def visualize_high_freq(high_freq_array):
        # 计算各方向高频分量的平均能量
        energy_map = np.mean(np.abs(high_freq_array), axis=0)
        # 归一化到[0,1]范围
        return (energy_map - energy_map.min()) / (energy_map.max() - energy_map.min())
    
    original_high_energy = visualize_high_freq(original_high_freq)
    residual_high_energy = visualize_high_freq(processed_high_freq)
    
    # 8. 可视化结果（扩展为6个子图）
    plt.figure(figsize=(18, 12))
    plt.subplot(231), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), plt.title("原始图像")
    plt.subplot(232), plt.imshow(LL, cmap='gray'), plt.title("低频分量")
    plt.subplot(233), plt.imshow(decay_map, cmap='hot'), plt.title("衰减系数图")
    plt.subplot(234), plt.imshow(np.mean(np.abs(np.stack([LH, HL, HH])), axis=0), cmap='viridis'), plt.title("高频分量")
    plt.subplot(235), plt.imshow(cv2.cvtColor(img_decayed, cv2.COLOR_BGR2RGB)), plt.title("结果图像")
    plt.subplot(236), plt.imshow(residual_high_energy, cmap='viridis'), 
    plt.title("衰减后剩余高频能量"), plt.colorbar()
    
    plt.tight_layout()
    plt.savefig('result_with_high_freq.png')
    plt.show()
    
    return img_decayed, residual_high_energy  # 同时返回剩余高频能量图

def generate_decay_timeseries(image_path, timestamps, decay_rate=0.7, high_freq_boost=1.5, wavelet='db2'):
    """
    生成多个时间点的衰减图像序列
    :param image_path: 输入图像路径
    :param timestamps: 时间戳列表，如 [0, 1, 2, 5, 10]
    :param decay_rate: 基础衰减率
    :param high_freq_boost: 高频增强系数
    :param wavelet: 小波类型
    :return: 衰减图像列表和高频能量图列表
    """
    decay_images = []
    high_freq_energies = []
    
    print(f"正在生成 {len(timestamps)} 个时间点的衰减序列...")
    
    for i, t in enumerate(timestamps):
        print(f"处理时间点 t={t} ({i+1}/{len(timestamps)})")
        
        # 生成当前时间点的衰减图像
        img_decayed, high_freq_energy = adaptive_frequency_decay(
            image_path=image_path,
            decay_rate=decay_rate,
            high_freq_boost=high_freq_boost,
            wavelet=wavelet,
            timestamp=t
        )
        
        # 保存图像
        output_filename = f"decay_t{t:03.1f}.jpg"
        cv2.imwrite(output_filename, img_decayed)
        
        # 保存高频特征图
        high_freq_vis = (high_freq_energy * 255).astype(np.uint8)
        high_freq_colored = cv2.applyColorMap(high_freq_vis, cv2.COLORMAP_JET)
        cv2.imwrite(f"high_freq_t{t:03.1f}.jpg", high_freq_colored)
        
        decay_images.append(img_decayed)
        high_freq_energies.append(high_freq_energy)
        
        print(f"已保存: {output_filename}")
    
    # 创建时间序列对比图
    create_timeseries_comparison(decay_images, high_freq_energies, timestamps)
    
    return decay_images, high_freq_energies

def create_timeseries_comparison(decay_images, high_freq_energies, timestamps):
    """创建时间序列对比可视化"""
    n_images = len(decay_images)
    
    # 创建大图：上排显示衰减图像，下排显示高频能量
    fig, axes = plt.subplots(2, n_images, figsize=(4*n_images, 8))
    
    for i, (img, hf_energy, t) in enumerate(zip(decay_images, high_freq_energies, timestamps)):
        # 上排：衰减图像
        axes[0, i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        axes[0, i].set_title(f"t = {t}")
        axes[0, i].axis('off')
        
        # 下排：高频能量
        im = axes[1, i].imshow(hf_energy, cmap='viridis')
        axes[1, i].set_title(f"高频能量 t = {t}")
        axes[1, i].axis('off')
        plt.colorbar(im, ax=axes[1, i], fraction=0.046, pad=0.04)
    
    plt.suptitle("高频信息抗衰减时间序列", fontsize=16)
    plt.tight_layout()
    plt.savefig('decay_timeseries_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("时间序列对比图已保存为: decay_timeseries_comparison.png")

if __name__ == "__main__":
    # 定义时间戳序列：从原始图像(t=0)到严重衰减(t=10)
    timestamps = [0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0]
    
    # 生成衰减时间序列
    decay_images, high_freq_energies = generate_decay_timeseries(
        image_path="e65dfaf4ac1ec7fc28b51284ca625e6.jpg",
        timestamps=timestamps,
        decay_rate=0.5,
        high_freq_boost=1.5,
        wavelet='db2'
    )
    
    print(f"\n完成！生成了 {len(timestamps)} 个时间点的衰减图像")
    print("文件命名格式: decay_t000.0.jpg, high_freq_t000.0.jpg")




# import cv2
# import numpy as np
# import pywt
# import matplotlib.pyplot as plt
# from matplotlib.colors import LinearSegmentedColormap

# def adaptive_frequency_decay(image_path, decay_rate=0, high_freq_boost=1.2, wavelet='haar'):
#     """自适应高频保留的图像衰减处理（完整实现）"""
#     # 1. 读取图像并转为浮点型
#     img = cv2.imread(image_path)
#     if img is None:
#         raise FileNotFoundError(f"图像 {image_path} 不存在")
#     h, w = img.shape[:2]
#     img_float = img.astype(np.float32) / 255.0

#     # 2. 尺寸预处理：填充至偶数尺寸
#     pad_h = (2 - h % 2) % 2
#     pad_w = (2 - w % 2) % 2
#     img_padded = np.pad(img_float, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')

#     # 3. 小波变换分离频段
#     coeffs = pywt.dwt2(img_padded, wavelet, axes=(0, 1))
#     LL, (LH, HL, HH) = coeffs
    
#     # 4. 计算原始高频分量（关键修复点）
#     original_high_freq = np.stack([LH, HL, HH])

#     # 5. 计算梯度图
#     gray_img = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
#     grad_x = cv2.Scharr(gray_img, cv2.CV_32F, 1, 0)
#     grad_y = cv2.Scharr(gray_img, cv2.CV_32F, 0, 1)
#     grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    
#     # 6. 缩放梯度图到高频分量尺寸
#     grad_mag_scaled = cv2.resize(grad_mag, (LH.shape[1], LH.shape[0]), interpolation=cv2.INTER_AREA)
#     decay_map = np.clip(grad_mag_scaled * high_freq_boost, 0.8, 1.0)
#     decay_map_3d = decay_map[..., np.newaxis]

#     # 7. 频段处理
#     LL_decayed = LL * decay_rate
#     LH_boosted = LH * decay_map_3d
#     HL_boosted = HL * decay_map_3d
#     HH_boosted = HH * decay_map_3d
    
#     # 8. 处理后的高频分量
#     processed_high_freq = np.stack([LH_boosted, HL_boosted, HH_boosted])

#     # 9. 重组图像并裁剪
#     coeffs_decayed = (LL_decayed, (LH_boosted, HL_boosted, HH_boosted))
#     img_decayed_padded = pywt.idwt2(coeffs_decayed, wavelet, axes=(0, 1))
#     img_decayed = img_decayed_padded[:h, :w]
#     img_decayed = np.clip(img_decayed * 255, 0, 255).astype(np.uint8)

#     # ===== 红橙色高频特征可视化（完整实现）=====
#     def visualize_high_freq_lines(high_freq_array):
#         # 计算高频能量图（合并分量和通道）
#         energy_map = np.sum(np.abs(high_freq_array), axis=(0, 3))
#         energy_map = (energy_map - energy_map.min()) / (energy_map.max() - energy_map.min()) * 255
#         energy_uint8 = energy_map.astype(np.uint8)
        
#         # 边缘检测（自适应阈值）
#         median = np.median(energy_uint8)
#         lower = int(max(0, 0.7 * median))
#         upper = int(min(255, 1.3 * median))
#         edges = cv2.Canny(energy_uint8, lower, upper)
        
#         # 创建红橙色渐变热力图
#         colors = [(0, 0, 0), (1, 0.5, 0), (1, 0, 0)]
#         fire_cmap = LinearSegmentedColormap.from_list('fire', colors, N=256)
#         heatmap = fire_cmap(energy_map/255)[:, :, :3]
        
#         # 强化边缘（红橙色）-- 修复形状问题
#         edge_mask = np.zeros_like(heatmap)
        
#         # 正确广播赋值：扩展[1, 0.25, 0]到(N, 3)形状
#         edge_color = np.array([1, 0.25, 0])  # 创建形状为(3,)的数组
#         edge_mask[edges > 0] = edge_color    # 自动广播到(N, 3)
        
#         # 融合热力图与边缘
#         final_vis = np.clip(heatmap * 0.8 + edge_mask * 0.9, 0, 1)
#         return final_vis, edges
    
#     # 生成可视化结果
#     _, original_edges = visualize_high_freq_lines(original_high_freq)
#     color_residual, residual_edges = visualize_high_freq_lines(processed_high_freq)
    
#     # 10. 专业级可视化布局
#     plt.figure(figsize=(20, 15))
    
#     # 第一行：核心结果
#     plt.subplot(231), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), 
#     plt.title("原始图像"), plt.axis('off')
    
#     plt.subplot(232), plt.imshow(cv2.cvtColor(img_decayed, cv2.COLOR_BGR2RGB)), 
#     plt.title("衰减后图像"), plt.axis('off')
    
#     plt.subplot(233), plt.imshow(color_residual), 
#     plt.title("红橙色高频特征"), plt.axis('off')
    
#     # 第二行：频域分析
#     plt.subplot(234), plt.imshow(LL, cmap='magma'), 
#     plt.title("低频分量"), plt.colorbar(fraction=0.046, pad=0.04)
    
#     plt.subplot(235), plt.imshow(np.mean(np.abs(original_high_freq), axis=0), cmap='viridis'), 
#     plt.title("原始高频能量"), plt.colorbar(fraction=0.046, pad=0.04)
    
#     plt.subplot(236), plt.imshow(decay_map, cmap='hot'), 
#     plt.title("衰减系数热力图"), plt.colorbar(fraction=0.046, pad=0.04)
    
#     plt.tight_layout()
#     plt.savefig('enhanced_visualization.png', dpi=300, bbox_inches='tight')
#     plt.show()
    
#     # 单独保存结果
#     cv2.imwrite("processed_image.jpg", img_decayed)
#     color_residual_bgr = (color_residual[:, :, ::-1] * 255).astype(np.uint8)
#     cv2.imwrite("high_freq_red_orange.jpg", color_residual_bgr)
    
#     return img_decayed, color_residual

# if __name__ == "__main__":
#     # 示例调用
#     result, high_freq_vis = adaptive_frequency_decay(
#         image_path="1.jpg",
#         decay_rate=0.7,
#         high_freq_boost=1.8,
#         wavelet='db2'
#     )