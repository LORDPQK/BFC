import math
import numpy as np
import random

# 输入参数
forget_percentage = 5  # 遗忘百分比（*10%）
matrix_size = 64  # 遗忘矩阵大小
forget_curve = "6.2*2.71828^(-x/0.23)"  # 遗忘曲线方程
noise_level = 10  # 噪声水平

def generate_1000_equations():
    """生成1000个不同类型的方程"""
    equations = []
    
    # 设置随机种子以确保结果可重现
    random.seed(42)
    
    # 1. 线性方程 (200个)
    for i in range(200):
        a = random.uniform(0.1, 3.0)
        b = random.uniform(-10, 50)
        equations.append(f"{a:.3f}*x + {b:.3f}")
    
    # 2. 二次方程 (150个)
    for i in range(150):
        a = random.uniform(0.001, 0.1)
        b = random.uniform(-2, 5)
        c = random.uniform(0, 30)
        equations.append(f"{a:.4f}*x^2 + {b:.3f}*x + {c:.3f}")
    
    # 3. 三次方程 (100个)
    for i in range(100):
        a = random.uniform(0.0001, 0.01)
        b = random.uniform(-0.1, 0.2)
        c = random.uniform(-3, 6)
        d = random.uniform(5, 25)
        equations.append(f"{a:.5f}*x^3 + {b:.4f}*x^2 + {c:.3f}*x + {d:.3f}")
    
    # 4. 三角函数 (150个)
    for i in range(150):
        amp = random.uniform(5, 15)
        freq = random.uniform(0.05, 0.2)
        phase = random.uniform(0, 2*math.pi)
        offset = random.uniform(10, 40)
        func_type = random.choice(['sin', 'cos'])
        equations.append(f"{amp:.3f}*{func_type}({freq:.4f}*x + {phase:.4f}) + {offset:.3f}")
    
    # 5. 指数函数 (100个)
    for i in range(100):
        base = random.uniform(0.5, 3.0)
        exp_coeff = random.uniform(-0.1, 0.1)
        offset = random.uniform(5, 30)
        equations.append(f"{base:.3f}*2.71828^({exp_coeff:.4f}*x) + {offset:.3f}")
    
    # 6. 对数函数 (80个)
    for i in range(80):
        coeff = random.uniform(2, 10)
        shift = random.uniform(0.1, 5)
        offset = random.uniform(5, 25)
        equations.append(f"{coeff:.3f}*log(x + {shift:.3f}) + {offset:.3f}")
    
    # 7. 平方根函数 (70个)
    for i in range(70):
        coeff = random.uniform(1, 8)
        inner_coeff = random.uniform(0.5, 4)
        offset = random.uniform(8, 35)
        equations.append(f"{coeff:.3f}*sqrt({inner_coeff:.3f}*x) + {offset:.3f}")
    
    # 8. 混合函数 (80个)
    for i in range(80):
        # 线性 + 三角
        a1 = random.uniform(0.2, 1.5)
        b1 = random.uniform(5, 20)
        a2 = random.uniform(2, 8)
        freq = random.uniform(0.08, 0.15)
        equations.append(f"{a1:.3f}*x + {b1:.3f} + {a2:.3f}*sin({freq:.4f}*x)")
    
    # 9. 反比例函数 (70个)
    for i in range(70):
        coeff = random.uniform(50, 200)
        offset = random.uniform(10, 30)
        shift = random.uniform(1, 5)
        equations.append(f"{coeff:.3f}/(x + {shift:.3f}) + {offset:.3f}")
    
    return equations

def create_function(expression):
    """将文本表达式转换为计算机函数"""
    def f(x):
        try:
            # 避免除零和负数开方
            if x <= 0 and ('log' in expression or 'sqrt' in expression):
                return float('inf')
            
            # 替换数学符号和函数
            expr = expression.replace('^', '**')
            expr = expr.replace('x', str(x))
            expr = expr.replace('log', 'math.log')
            expr = expr.replace('sin', 'math.sin')
            expr = expr.replace('cos', 'math.cos')
            expr = expr.replace('sqrt', 'math.sqrt')
            expr = expr.replace('2.71828', 'math.e')
            
            result = eval(expr)
            
            # 检查结果是否在合理范围内
            if math.isnan(result) or math.isinf(result) or result < -1000 or result > 1000:
                return float('inf')
            
            return result
        except:
            return float('inf')
    return f

def calculate_quantization_error(function, matrix_size):
    """计算量化误差"""
    errors = []
    valid_points = 0
    
    for x in range(matrix_size):
        try:
            y_real = function(x)
            
            # 跳过无效值
            if math.isinf(y_real) or math.isnan(y_real):
                continue
                
            y_discrete = int(y_real + 0.5)
            error = abs(y_real - y_discrete)
            errors.append(error)
            valid_points += 1
        except:
            continue
    
    if len(errors) == 0:
        return 0, 0, 0, 0
    
    rms_error = math.sqrt(sum(e*e for e in errors) / len(errors))
    max_error = max(errors)
    mean_error = sum(errors) / len(errors)
    
    return rms_error, max_error, mean_error, valid_points

def calculate_domain_relative_error(function, matrix_size):
    """计算基于定义域的相对误差"""
    try:
        rms_error, _, _, valid_points = calculate_quantization_error(function, matrix_size)
        
        # 如果有效点太少，认为函数不适合
        if valid_points < matrix_size * 0.5:
            return float('inf')
        
        domain_range = matrix_size - 1
        relative_error = rms_error / domain_range if domain_range > 0 else 0
        return relative_error
    except:
        return float('inf')

def analyze_1000_equations():
    """分析1000个方程的误差"""
    print("=== 生成1000个方程 ===")
    equations = generate_1000_equations()
    print(f"成功生成 {len(equations)} 个方程")
    
    print("\n=== 开始误差分析 ===")
    print("这可能需要一些时间...")
    
    valid_equations = []
    error_results = []
    
    # 分批处理以显示进度
    batch_size = 100
    for batch_start in range(0, len(equations), batch_size):
        batch_end = min(batch_start + batch_size, len(equations))
        print(f"处理方程 {batch_start+1}-{batch_end}...")
        
        for i in range(batch_start, batch_end):
            eq = equations[i]
            try:
                func = create_function(eq)
                
                # 计算误差
                rms_error, max_error, mean_error, valid_points = calculate_quantization_error(func, matrix_size)
                domain_rel_error = calculate_domain_relative_error(func, matrix_size)
                
                # 只保留有效的方程（有足够多的有效点且误差不是无穷大）
                if valid_points >= matrix_size * 0.5 and not math.isinf(domain_rel_error):
                    valid_equations.append(eq)
                    error_results.append({
                        'equation_id': len(valid_equations),
                        'equation': eq,
                        'rms_error': rms_error,
                        'max_error': max_error,
                        'mean_error': mean_error,
                        'domain_relative_error': domain_rel_error,
                        'valid_points': valid_points
                    })
            except Exception as e:
                # 跳过无法处理的方程
                continue
    
    print(f"\n有效方程数量: {len(valid_equations)} / {len(equations)}")
    
    return error_results

def statistical_analysis(error_results):
    """统计分析结果"""
    if not error_results:
        print("没有有效的误差数据")
        return
    
    print(f"\n=== 1000方程组误差统计分析 ===")
    print(f"有效方程数量: {len(error_results)}")
    
    # 提取误差数据
    domain_errors = [r['domain_relative_error'] for r in error_results]
    rms_errors = [r['rms_error'] for r in error_results]
    max_errors = [r['max_error'] for r in error_results]
    
    # 基本统计
    avg_domain_error = sum(domain_errors) / len(domain_errors)
    min_domain_error = min(domain_errors)
    max_domain_error = max(domain_errors)
    median_domain_error = sorted(domain_errors)[len(domain_errors)//2]
    
    print(f"\n定义域相对误差统计:")
    print(f"平均相对误差: {avg_domain_error:.6f} ({avg_domain_error*100:.4f}%)")
    print(f"最小相对误差: {min_domain_error:.6f} ({min_domain_error*100:.4f}%)")
    print(f"最大相对误差: {max_domain_error:.6f} ({max_domain_error*100:.4f}%)")
    print(f"中位数相对误差: {median_domain_error:.6f} ({median_domain_error*100:.4f}%)")
    
    # 标准差
    variance = sum((e - avg_domain_error)**2 for e in domain_errors) / len(domain_errors)
    std_dev = math.sqrt(variance)
    print(f"标准差: {std_dev:.6f} ({std_dev*100:.4f}%)")
    
    # 误差分布统计
    print(f"\n误差分布:")
    ranges = [(0, 0.001), (0.001, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, float('inf'))]
    range_names = ["极低(<0.1%)", "很低(0.1%-0.5%)", "低(0.5%-1%)", "中等(1%-2%)", "高(>2%)"]
    
    for i, (low, high) in enumerate(ranges):
        count = sum(1 for e in domain_errors if low <= e < high)
        percentage = count / len(domain_errors) * 100
        print(f"{range_names[i]}: {count} 个方程 ({percentage:.1f}%)")
    
    # 精度等级评估
    print(f"\n=== 整体精度评估 ===")
    if avg_domain_error < 0.001:
        precision_level = "极高精度"
    elif avg_domain_error < 0.005:
        precision_level = "高精度"
    elif avg_domain_error < 0.01:
        precision_level = "中等精度"
    elif avg_domain_error < 0.02:
        precision_level = "低精度但可用"
    else:
        precision_level = "精度不足"
    
    print(f"整体精度等级: {precision_level}")
    
    # 与噪声水平比较
    noise_ratio = noise_level / 100
    print(f"\n=== 与噪声水平比较 ===")
    print(f"噪声水平: {noise_ratio:.2f} ({noise_level}%)")
    
    if avg_domain_error < noise_ratio * 0.1:
        print("✓ 计算误差远小于噪声水平，精度优秀")
    elif avg_domain_error < noise_ratio * 0.5:
        print("✓ 计算误差小于噪声水平，精度良好")
    elif avg_domain_error < noise_ratio:
        print("⚠ 计算误差接近噪声水平，精度可接受")
    else:
        print("⚠ 计算误差超过噪声水平，建议优化")
    
    # 矩阵大小建议
    print(f"\n=== 矩阵大小建议 ===")
    if avg_domain_error > 0.01:
        suggested_size = int(matrix_size * math.sqrt(avg_domain_error / 0.01))
        print(f"建议矩阵大小: {suggested_size}×{suggested_size} (目标误差<1%)")
    else:
        print("✓ 当前64×64矩阵大小完全适合")
        
        # 可以尝试更小的矩阵
        if avg_domain_error < 0.005:
            smaller_size = 32
            estimated_error = avg_domain_error * (matrix_size / smaller_size)
            print(f"可尝试更小矩阵: {smaller_size}×{smaller_size} (预估误差: {estimated_error*100:.3f}%)")
    
    return {
        'total_equations': len(error_results),
        'average_relative_error': avg_domain_error,
        'minimum_relative_error': min_domain_error,
        'maximum_relative_error': max_domain_error,
        'median_relative_error': median_domain_error,
        'standard_deviation': std_dev,
        'precision_level': precision_level
    }

def main():
    print("=== 大规模遗忘算法误差分析 (1000方程) ===")
    print(f"参数设置:")
    print(f"遗忘百分比: {forget_percentage}×10%")
    print(f"矩阵大小: {matrix_size}×{matrix_size}")
    print(f"遗忘曲线: {forget_curve}")
    print(f"噪声水平: {noise_level}%")
    print("="*60)
    
    # 分析1000个方程
    error_results = analyze_1000_equations()
    
    # 统计分析
    stats = statistical_analysis(error_results)
    
    return stats

if __name__ == "__main__":
    results = main()