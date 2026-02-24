import math
import numpy as np

# 输入参数
forget_percentage = 5  # 遗忘百分比（*10%）
matrix_size = 64  # 遗忘矩阵大小
forget_curve = "6.2*2.71828^(-x/0.23)"  # 遗忘曲线方程
noise_level = 10  # 噪声水平

# 设计10组方程，每组2-3个方程
equation_groups = [
    # 组1: 线性方程组
    ["x + 2", "2*x - 1"],
    
    # 组2: 二次方程组
    ["0.1*x^2 + 5", "x + 10"],
    
    # 组3: 三角函数组
    ["10*sin(0.1*x) + 20", "x + 15"],
    
    # 组4: 指数函数组
    ["2.71828^(0.05*x)", "30 - x"],
    
    # 组5: 对数函数组
    ["5*log(x+1) + 10", "25 - 0.5*x"],
    
    # 组6: 复合函数组
    ["x^2*0.02 + x + 5", "20 - x", "x*1.5 + 8"],
    
    # 组7: 高次多项式组
    ["0.001*x^3 - 0.1*x^2 + 2*x + 10", "35 - 0.8*x"],
    
    # 组8: 混合三角函数组
    ["15 + 8*cos(0.08*x)", "x*0.7 + 5", "25 - 0.3*x"],
    
    # 组9: 复杂指数组
    ["20*2.71828^(-0.03*x) + 5", "x + 8"],
    
    # 组10: 综合函数组
    ["sqrt(x*4) + 10", "30 - x*0.6", "x*0.8 + 12"]
]

def create_function(expression):
    """将文本表达式转换为计算机函数"""
    def f(x):
        try:
            # 替换数学符号和函数
            expr = expression.replace('^', '**')
            expr = expr.replace('x', str(x))
            expr = expr.replace('log', 'math.log')
            expr = expr.replace('sin', 'math.sin')
            expr = expr.replace('cos', 'math.cos')
            expr = expr.replace('sqrt', 'math.sqrt')
            expr = expr.replace('2.71828', 'math.e')
            return eval(expr)
        except:
            return 0
    return f

def calculate_quantization_error(function, matrix_size):
    """计算量化误差"""
    errors = []
    for x in range(matrix_size):
        try:
            y_real = function(x)
            y_discrete = int(y_real + 0.5)
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

def calculate_domain_relative_error(function, matrix_size):
    """计算基于定义域的相对误差（适合模糊计算）"""
    try:
        rms_error, _, _ = calculate_quantization_error(function, matrix_size)
        # 定义域范围是 [0, matrix_size-1]
        domain_range = matrix_size - 1
        relative_error = rms_error / domain_range if domain_range > 0 else 0
        return relative_error
    except:
        return 0

def find_intersection_points(functions, matrix_size):
    """寻找方程组的交点（模拟遗忘算法的求解过程）"""
    intersections = []
    
    # 对于每对函数，寻找交点
    for i in range(len(functions)):
        for j in range(i+1, len(functions)):
            func1, func2 = functions[i], functions[j]
            
            # 在定义域内搜索交点
            for x in range(matrix_size):
                try:
                    y1 = func1(x)
                    y2 = func2(x)
                    
                    # 如果函数值接近（在1个单位内），认为是交点
                    if abs(y1 - y2) < 1.0 and 0 <= y1 < matrix_size and 0 <= y2 < matrix_size:
                        intersections.append((x, (y1 + y2) / 2))
                except:
                    continue
    
    return intersections

def analyze_equation_group(group_equations, group_id):
    """分析单组方程的误差"""
    print(f"\n=== 组 {group_id}: {group_equations} ===")
    
    # 创建函数对象
    functions = []
    for eq in group_equations:
        try:
            func = create_function(eq)
            functions.append(func)
        except Exception as e:
            print(f"警告: 无法解析方程 '{eq}': {e}")
            continue
    
    if len(functions) == 0:
        return None
    
    # 计算每个函数的误差
    function_errors = []
    for i, func in enumerate(functions):
        rms_error, max_error, mean_error = calculate_quantization_error(func, matrix_size)
        domain_rel_error = calculate_domain_relative_error(func, matrix_size)
        
        print(f"方程 {i+1}: {group_equations[i]}")
        print(f"  RMS误差: {rms_error:.6f}")
        print(f"  最大误差: {max_error:.6f}")
        print(f"  定义域相对误差: {domain_rel_error:.6f} ({domain_rel_error*100:.4f}%)")
        
        function_errors.append({
            'equation': group_equations[i],
            'rms_error': rms_error,
            'max_error': max_error,
            'domain_relative_error': domain_rel_error
        })
    
    # 寻找交点并分析交点误差
    intersections = find_intersection_points(functions, matrix_size)
    print(f"找到 {len(intersections)} 个交点")
    
    # 计算组平均误差
    if function_errors:
        avg_domain_error = sum(e['domain_relative_error'] for e in function_errors) / len(function_errors)
        max_domain_error = max(e['domain_relative_error'] for e in function_errors)
        
        print(f"组平均定义域相对误差: {avg_domain_error:.6f} ({avg_domain_error*100:.4f}%)")
        print(f"组最大定义域相对误差: {max_domain_error:.6f} ({max_domain_error*100:.4f}%)")
        
        return {
            'group_id': group_id,
            'equations': group_equations,
            'function_errors': function_errors,
            'avg_domain_error': avg_domain_error,
            'max_domain_error': max_domain_error,
            'intersections': intersections
        }
    
    return None

def main():
    print("=== 遗忘算法10组方程误差分析 ===")
    print(f"参数设置:")
    print(f"遗忘百分比: {forget_percentage}×10%")
    print(f"矩阵大小: {matrix_size}×{matrix_size}")
    print(f"遗忘曲线: {forget_curve}")
    print(f"噪声水平: {noise_level}%")
    print("="*60)
    
    all_results = []
    
    # 分析每组方程
    for i, group in enumerate(equation_groups, 1):
        result = analyze_equation_group(group, i)
        if result:
            all_results.append(result)
    
    # 总体统计分析
    print(f"\n" + "="*60)
    print("=== 总体误差统计 ===")
    
    if all_results:
        # 计算所有组的平均误差
        all_avg_errors = [r['avg_domain_error'] for r in all_results]
        all_max_errors = [r['max_domain_error'] for r in all_results]
        
        overall_avg_error = sum(all_avg_errors) / len(all_avg_errors)
        overall_min_error = min(all_avg_errors)
        overall_max_error = max(all_max_errors)
        
        print(f"10组方程的平均相对误差: {overall_avg_error:.6f} ({overall_avg_error*100:.4f}%)")
        print(f"10组方程的最小相对误差: {overall_min_error:.6f} ({overall_min_error*100:.4f}%)")
        print(f"10组方程的最大相对误差: {overall_max_error:.6f} ({overall_max_error*100:.4f}%)")
        
        # 精度等级评估
        print(f"\n=== 精度等级评估 ===")
        if overall_avg_error < 0.01:
            precision_level = "高精度"
        elif overall_avg_error < 0.05:
            precision_level = "中等精度"
        elif overall_avg_error < 0.1:
            precision_level = "低精度但可用"
        else:
            precision_level = "精度不足"
        
        print(f"整体精度等级: {precision_level}")
        
        # 遗忘算法适用性分析
        print(f"\n=== 遗忘算法适用性分析 ===")
        noise_ratio = noise_level / 100
        print(f"噪声水平: {noise_ratio:.2f}")
        
        if overall_avg_error < noise_ratio:
            print("✓ 计算误差小于噪声水平，精度满足要求")
        else:
            print("⚠ 计算误差接近或超过噪声水平，建议增大矩阵或降低噪声")
        
        # 矩阵大小建议
        if overall_avg_error > 0.01:
            suggested_size = int(matrix_size * math.sqrt(overall_avg_error / 0.01))
            print(f"建议矩阵大小: {suggested_size}×{suggested_size} (目标误差<1%)")
        else:
            print("✓ 当前64×64矩阵大小适合")
        
        return {
            'average_relative_error': overall_avg_error,
            'minimum_relative_error': overall_min_error,
            'maximum_relative_error': overall_max_error,
            'precision_level': precision_level
        }

if __name__ == "__main__":
    results = main()