import math
import numpy as np

# 输入数据
equations = ["x*2", "1"]  # y=x*2 和 y=1
forget_percentage = 5  # 遗忘百分比（*10%）
matrix_size = 64  # 遗忘矩阵大小
forget_curve = "6.2*2.71828^(-x/0.23)"  # 遗忘曲线方程
noise_level = 10  # 噪声水平

def create_function(expression):
    """将文本表达式转换为计算机函数"""
    def f(x):
        return eval(expression.replace('^', '**').replace('x', str(x)))
    return f

def calculate_quantization_error(function, matrix_size):
    """计算量化误差"""
    errors = []
    for x in range(matrix_size):
        try:
            y_real = function(x)           # 真实函数值
            y_discrete = int(y_real + 0.5) # 四舍五入到整数
            error = abs(y_real - y_discrete)
            errors.append(error)
        except:
            errors.append(0)
    
    if len(errors) == 0:
        return 0, 0, 0
    
    rms_error = math.sqrt(sum(e*e for e in errors) / len(errors))
    max_error = max(errors)
    mean_error = sum(errors) / len(errors)
    
    return rms_error, max_error, mean_error

def calculate_relative_error(function, matrix_size):
    """计算相对误差"""
    try:
        y_values = []
        for x in range(matrix_size):
            try:
                y_values.append(function(x))
            except:
                continue
        
        if len(y_values) == 0:
            return 0
            
        y_range = max(y_values) - min(y_values)
        
        if y_range == 0:
            return 0
        
        rms_error, _, _ = calculate_quantization_error(function, matrix_size)
        relative_error = rms_error / y_range
        return relative_error
    except:
        return 0

def main():
    print("=== 遗忘算法离散化误差分析 ===")
    print(f"输入参数:")
    print(f"方程组: {equations}")
    print(f"矩阵大小: {matrix_size}×{matrix_size}")
    print(f"遗忘百分比: {forget_percentage}×10%")
    print(f"遗忘曲线: {forget_curve}")
    print(f"噪声水平: {noise_level}")
    print("\n" + "="*50)
    
    # 创建函数对象
    functions = []
    for eq in equations:
        try:
            func = create_function(eq)
            functions.append((eq, func))
        except Exception as e:
            print(f"警告: 无法解析方程 '{eq}': {e}")
    
    # 分析每个函数的误差
    total_errors = []
    
    for i, (eq_str, func) in enumerate(functions):
        print(f"\n方程 {i+1}: y = {eq_str}")
        print("-" * 30)
        
        # 量化误差
        rms_error, max_error, mean_error = calculate_quantization_error(func, matrix_size)
        print(f"量化误差:")
        print(f"  RMS误差: {rms_error:.6f}")
        print(f"  最大误差: {max_error:.6f}")
        print(f"  平均误差: {mean_error:.6f}")
        
        # 相对误差
        rel_error = calculate_relative_error(func, matrix_size)
        print(f"相对误差: {rel_error:.6f} ({rel_error*100:.4f}%)")
        
        # 误差评估
        if rel_error < 0.001:
            error_level = "极低"
        elif rel_error < 0.01:
            error_level = "低"
        elif rel_error < 0.05:
            error_level = "中等"
        else:
            error_level = "高"
        
        print(f"误差等级: {error_level}")
        
        total_errors.append({
            'equation': eq_str,
            'rms_error': rms_error,
            'relative_error': rel_error
        })
    
    # 总体误差分析
    print(f"\n" + "="*50)
    print("总体误差分析:")
    
    if total_errors:
        avg_relative_error = sum(e['relative_error'] for e in total_errors) / len(total_errors)
        max_relative_error = max(e['relative_error'] for e in total_errors)
        
        print(f"平均相对误差: {avg_relative_error:.6f} ({avg_relative_error*100:.4f}%)")
        print(f"最大相对误差: {max_relative_error:.6f} ({max_relative_error*100:.4f}%)")
        
        # 系统建议
        print(f"\n系统建议:")
        if avg_relative_error < 0.001:
            print("✓ 当前矩阵大小足够，误差极小")
        elif avg_relative_error < 0.01:
            print("✓ 当前矩阵大小合适，误差可接受")
        else:
            print("⚠ 建议增大矩阵大小以提高精度")

if __name__ == "__main__":
    main()