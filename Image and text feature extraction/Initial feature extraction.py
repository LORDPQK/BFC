import cv2
import numpy as np
import pywt
import matplotlib.pyplot as plt

def adaptive_frequency_decay(image_path, decay_rate=0.9, high_freq_boost=1.2, wavelet='haar'):
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

    # 6. 频段处理
    LL_decayed = LL * decay_rate
    LH_boosted = LH * decay_map_3d
    HL_boosted = HL * decay_map_3d
    HH_boosted = HH * decay_map_3d

    # 7. 重组图像并裁剪回原始尺寸
    coeffs_decayed = (LL_decayed, (LH_boosted, HL_boosted, HH_boosted))
    img_decayed_padded = pywt.idwt2(coeffs_decayed, wavelet, axes=(0, 1))
    img_decayed = img_decayed_padded[:h, :w]  # 移除填充部分
    img_decayed = np.clip(img_decayed * 255, 0, 255).astype(np.uint8)
    

    # 8. 可视化结果
    plt.figure(figsize=(15, 10))
    plt.subplot(231), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), plt.title("原始图像")
    plt.subplot(232), plt.imshow(LL, cmap='gray'), plt.title("低频分量")
    plt.subplot(233), plt.imshow(decay_map, cmap='hot'), plt.title("衰减系数图")
    plt.subplot(234), plt.imshow(np.mean(np.abs(np.stack([LH, HL, HH])), axis=0), cmap='viridis'), plt.title("高频分量")
    plt.subplot(235), plt.imshow(cv2.cvtColor(img_decayed, cv2.COLOR_BGR2RGB)), plt.title("结果图像")
    plt.tight_layout()
    plt.savefig('result.png')
    plt.show()
    return img_decayed

if __name__ == "__main__":
    result = adaptive_frequency_decay(
        image_path="2.jpg",  # 替换为实际路径
        decay_rate=0.7,
        high_freq_boost=1.5,
        wavelet='db2'
    )
    cv2.imwrite("processed_image.jpg", result)