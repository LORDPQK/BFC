import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def gradual_blur_stages(image_path, output_prefix="blurred_stage", blur_method="gaussian"):
    """
    对输入图像进行5个阶段的渐进式模糊处理
    :param image_path: 输入图像路径
    :param output_prefix: 输出文件名前缀
    :param blur_method: 模糊方法 ("gaussian", "motion", "average", "median")
    :return: 模糊图像列表
    """
    # 读取原始图像
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图像: {image_path}")
    
    print(f"开始处理图像: {image_path}")
    print(f"图像尺寸: {img.shape}")
    
    # 定义5个模糊强度级别
    blur_levels = [
        {"stage": 0, "intensity": 0, "description": "原始图像"},
        {"stage": 1, "intensity": 5, "description": "轻微模糊"},
        {"stage": 2, "intensity": 15, "description": "中等模糊"},
        {"stage": 3, "intensity": 35, "description": "明显模糊"},
        {"stage": 4, "intensity": 75, "description": "严重模糊"}
    ]
    
    blurred_images = []
    
    for level in blur_levels:
        stage = level["stage"]
        intensity = level["intensity"]
        description = level["description"]
        
        print(f"处理阶段 {stage}: {description} (强度: {intensity})")
        
        if stage == 0:
            # 阶段0：保持原始图像
            blurred_img = img.copy()
        else:
            # 根据选择的模糊方法处理
            if blur_method == "gaussian":
                # 高斯模糊：最常用的模糊效果
                kernel_size = intensity if intensity % 2 == 1 else intensity + 1  # 确保奇数
                blurred_img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
                
            elif blur_method == "motion":
                # 运动模糊：模拟相机抖动
                kernel = np.zeros((intensity, intensity))
                kernel[int((intensity-1)/2), :] = np.ones(intensity)
                kernel = kernel / intensity
                blurred_img = cv2.filter2D(img, -1, kernel)
                
            elif blur_method == "average":
                # 均值模糊：简单平均
                blurred_img = cv2.blur(img, (intensity, intensity))
                
            elif blur_method == "median":
                # 中值模糊：保边去噪
                kernel_size = intensity if intensity % 2 == 1 else intensity + 1
                blurred_img = cv2.medianBlur(img, kernel_size)
                
            else:
                raise ValueError(f"不支持的模糊方法: {blur_method}")
        
        # 保存图像
        output_filename = f"{output_prefix}_{stage}_{blur_method}.jpg"
        cv2.imwrite(output_filename, blurred_img)
        blurred_images.append(blurred_img)
        
        print(f"已保存: {output_filename}")
    
    # 创建对比可视化
    create_blur_comparison(blurred_images, blur_levels, blur_method, output_prefix)
    
    return blurred_images

def create_blur_comparison(blurred_images, blur_levels, blur_method, output_prefix):
    """创建模糊阶段对比图"""
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    
    for i, (img, level) in enumerate(zip(blurred_images, blur_levels)):
        # 转换BGR到RGB用于matplotlib显示
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        axes[i].imshow(img_rgb)
        axes[i].set_title(f"阶段 {level['stage']}: {level['description']}\n强度: {level['intensity']}")
        axes[i].axis('off')
    
    plt.suptitle(f"渐进式模糊效果对比 - {blur_method.upper()}方法", fontsize=16)
    plt.tight_layout()
    
    comparison_filename = f"{output_prefix}_comparison_{blur_method}.png"
    plt.savefig(comparison_filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"对比图已保存: {comparison_filename}")

def advanced_blur_effects(image_path, output_prefix="advanced_blur"):
    """
    高级模糊效果：结合多种模糊技术
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图像: {image_path}")
    
    print("生成高级模糊效果...")
    
    # 定义高级模糊效果
    effects = [
        {"name": "original", "description": "原始图像"},
        {"name": "selective_blur", "description": "选择性模糊（保留边缘）"},
        {"name": "radial_blur", "description": "径向模糊"},
        {"name": "lens_blur", "description": "镜头模糊"},
        {"name": "surface_blur", "description": "表面模糊"}
    ]
    
    processed_images = []
    
    for i, effect in enumerate(effects):
        if effect["name"] == "original":
            processed_img = img.copy()
            
        elif effect["name"] == "selective_blur":
            # 选择性模糊：保留强边缘，模糊平滑区域
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edges = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
            edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            blurred = cv2.GaussianBlur(img, (21, 21), 0)
            processed_img = np.where(edges_3ch > 0, img, blurred)
            
        elif effect["name"] == "radial_blur":
            # 径向模糊：从中心向外模糊
            h, w = img.shape[:2]
            center_x, center_y = w//2, h//2
            
            processed_img = img.copy().astype(np.float32)
            for radius in range(5, 25, 5):
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(mask, (center_x, center_y), radius, 255, -1)
                cv2.circle(mask, (center_x, center_y), radius-5, 0, -1)
                
                blurred_ring = cv2.GaussianBlur(img, (radius//2*2+1, radius//2*2+1), 0)
                processed_img = np.where(mask[..., np.newaxis] > 0, blurred_ring, processed_img)
            
            processed_img = processed_img.astype(np.uint8)
            
        elif effect["name"] == "lens_blur":
            # 镜头模糊：模拟景深效果
            kernel = np.ones((15,15), np.float32) / 225
            processed_img = cv2.filter2D(img, -1, kernel)
            
        elif effect["name"] == "surface_blur":
            # 表面模糊：保持边缘清晰度
            processed_img = cv2.edgePreservingFilter(img, flags=2, sigma_s=50, sigma_r=0.4)
        
        # 保存图像
        output_filename = f"{output_prefix}_{i}_{effect['name']}.jpg"
        cv2.imwrite(output_filename, processed_img)
        processed_images.append(processed_img)
        
        print(f"已生成: {effect['description']} -> {output_filename}")
    
    # 创建高级效果对比图
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    
    for i, (img, effect) in enumerate(zip(processed_images, effects)):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        axes[i].imshow(img_rgb)
        axes[i].set_title(effect['description'])
        axes[i].axis('off')
    
    plt.suptitle("高级模糊效果对比", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_advanced_comparison.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    return processed_images

if __name__ == "__main__":
    # 输入图像路径（请修改为你的图像路径）
    input_image = "2.png"  # 替换为你的图像文件
    
    if not os.path.exists(input_image):
        print(f"错误: 找不到图像文件 {input_image}")
        print("请确保图像文件存在，或修改 input_image 变量")
    else:
        print("=== 基础渐进式模糊 ===")
        
        # 1. 高斯模糊（推荐）
        gaussian_images = gradual_blur_stages(
            image_path=input_image,
            output_prefix="blur_gaussian",
            blur_method="gaussian"
        )
        
        # 2. 运动模糊
        motion_images = gradual_blur_stages(
            image_path=input_image,
            output_prefix="blur_motion", 
            blur_method="motion"
        )
        
        # 3. 均值模糊
        average_images = gradual_blur_stages(
            image_path=input_image,
            output_prefix="blur_average",
            blur_method="average"
        )
        
        print("\n=== 高级模糊效果 ===")
        
        # 4. 高级模糊效果
        advanced_images = advanced_blur_effects(
            image_path=input_image,
            output_prefix="advanced_blur"
        )
        
        print(f"\n完成！共生成了 {5*3 + 5} 个模糊图像")
        print("文件命名格式:")
        print("- 基础模糊: blur_[method]_[stage]_[method].jpg")
        print("- 高级模糊: advanced_blur_[stage]_[effect].jpg")
        print("- 对比图: *_comparison_*.png")