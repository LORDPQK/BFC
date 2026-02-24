import math
import numpy as np
import random
import matplotlib.pyplot as plt

# 输入参数
forget_percentage = 5  # 遗忘百分比（*10%）
matrix_size = 64  # 遗忘矩阵大小
forget_curve = "6.2*2.71828^(-x/0.23)"  # 遗忘曲线方程
noise_level = 10  # 噪声水平

def generate_solvable_1000_equations():
    """生成1000个有解的方程组"""
    equations = []
    
    # 设置随机种子以确保结果可重现
    random.seed(42)
    
    # 预设几个解点，让方程围绕这些点构造
    solution_points = [
        (10, 20), (15, 25), (20, 30), (25, 35), (30, 40),
        (35, 45), (40, 50), (45, 55), (50, 60), (8, 18)
    ]
    
    equations_per_point = 100  # 每个解点100个方程
    
    for point_idx, (sol_x, sol_y) in enumerate(solution_points):
        print(f"为解点 ({sol_x}, {sol_y}) 生成方程...")
        
        for i in range(equations_per_point):
            eq_type = i % 10  # 10种不同类型的方程
            
            if eq_type == 0:  # 线性方程: y = ax + b
                a = random.uniform(0.5, 3.0)
                b = sol_y - a * sol_x + random.uniform(-2, 2)
                equations.append(f"{a:.4f}*x + {b:.4f}")
                
            elif eq_type == 1:  # 二次方程: y = ax^2 + bx + c
                a = random.uniform(0.001, 0.01)
                b = random.uniform(-0.5, 0.5)
                c = sol_y - a * sol_x**2 - b * sol_x + random.uniform(-1, 1)
                equations.append(f"{a:.6f}*x^2 + {b:.4f}*x + {c:.4f}")
                
            elif eq_type == 2:  # 三角函数: y = A*sin(wx + φ) + D
                A = random.uniform(1, 3)
                w = random.uniform(0.1, 0.3)
                phi = random.uniform(0, 2*math.pi)
                D = sol_y - A * math.sin(w * sol_x + phi) + random.uniform(-1, 1)
                equations.append(f"{A:.4f}*sin({w:.4f}*x + {phi:.4f}) + {D:.4f}")
                
            elif eq_type == 3:  # 余弦函数
                A = random.uniform(1, 3)
                w = random.uniform(0.1, 0.3)
                phi = random.uniform(0, 2*math.pi)
                D = sol_y - A * math.cos(w * sol_x + phi) + random.uniform(-1, 1)
                equations.append(f"{A:.4f}*cos({w:.4f}*x + {phi:.4f}) + {D:.4f}")
                
            elif eq_type == 4:  # 指数函数: y = A*e^(bx) + C
                b = random.uniform(-0.05, 0.05)
                A = random.uniform(0.5, 2.0)
                C = sol_y - A * math.exp(b * sol_x) + random.uniform(-1, 1)
                equations.append(f"{A:.4f}*2.71828^({b:.6f}*x) + {C:.4f}")
                
            elif eq_type == 5:  # 对数函数: y = A*log(x + B) + C
                A = random.uniform(1, 5)
                B = random.uniform(0.1, 2)
                C = sol_y - A * math.log(sol_x + B) + random.uniform(-1, 1)
                equations.append(f"{A:.4f}*log(x + {B:.4f}) + {C:.4f}")
                
            elif eq_type == 6:  # 平方根函数: y = A*sqrt(Bx + C) + D
                B = random.uniform(0.5, 2)
                A = random.uniform(1, 4)
                C = random.uniform(0.1, 1)
                D = sol_y - A * math.sqrt(B * sol_x + C) + random.uniform(-1, 1)
                equations.append(f"{A:.4f}*sqrt({B:.4f}*x + {C:.4f}) + {D:.4f}")
                
            elif eq_type == 7:  # 反比例函数: y = A/(x + B) + C
                A = random.uniform(10, 50)
                B = random.uniform(0.5, 2)
                C = sol_y - A / (sol_x + B) + random.uniform(-1, 1)
                equations.append(f"{A:.4f}/(x + {B:.4f}) + {C:.4f}")
                
            elif eq_type == 8:  # 三次函数: y = ax^3 + bx^2 + cx + d
                a = random.uniform(0.0001, 0.001)
                b = random.uniform(-0.01, 0.01)
                c = random.uniform(-0.5, 0.5)
                d = sol_y - a * sol_x**3 - b * sol_x**2 - c * sol_x + random.uniform(-1, 1)
                equations.append(f"{a:.7f}*x^3 + {b:.6f}*x^2 + {c:.4f}*x + {d:.4f}")
                
            else:  # 混合函数: y = ax + b + c*sin(dx)
                a = random.uniform(0.3, 1.5)
                b = random.uniform(-5, 5)
                c = random.uniform(0.5, 2)
                d = random.uniform(0.2, 0.5)
                base_y = a * sol_x + b + c * math.sin(d * sol_x)
                offset = sol_y - base_y + random.uniform(-1, 1)
                equations.append(f"{a:.4f}*x + {b:.4f} + {c:.4f}*sin({d:.4f}*x) + {offset:.4f}")
    
    return equations, solution_points

def create_function(expression):
    """将文本表达式转换为计算机函数"""
    def f(x):
        try:
            # 避免无效计算
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
            
            # 检查结果范围
            if math.isnan(result) or math.isinf(result) or result < 0 or result >= matrix_size:
                return float('inf')
            
            return result
        except:
            return float('inf')
    return f

def create_forget_function(expression):
    """创建遗忘函数"""
    def f(t):
        try:
            expr = expression.replace('^', '**')
            expr = expr.replace('x', str(t))
            expr = expr.replace('2.71828', 'math.e')
            return eval(expr)
        except:
            return 0
    return f

def plus(function, matrix_size):
    """将单个函数映射到矩阵（遗忘算法的plus函数）"""
    D = np.zeros([matrix_size, matrix_size])
    
    for i in range(matrix_size):
        try:
            y = function(i)
            
            if math.isinf(y) or math.isnan(y) or y < 0 or y >= matrix_size:
                continue
            
            # 处理连续点之间的插值
            if i > 0:
                y_prev = function(i-1)
                if not (math.isinf(y_prev) or math.isnan(y_prev)):
                    y_min = max(0, min(int(y), int(y_prev)))
                    y_max = min(matrix_size-1, max(int(y), int(y_prev)))
                    
                    for j in range(y_min, y_max + 1):
                        D[i][j] = 1
            
            # 设置当前点
            y_int = int(y + 0.5)
            if 0 <= y_int < matrix_size:
                D[i][y_int] = 1
                
        except:
            continue
    
    return D

def forget_algorithm_solve(equations, forget_curve_expr, time_steps, noise_threshold):
    """使用遗忘算法求解方程组"""
    print(f"开始遗忘算法求解...")
    print(f"方程数量: {len(equations)}")
    print(f"矩阵大小: {matrix_size}×{matrix_size}")
    print(f"时间步数: {time_steps}")
    
    # 创建函数对象
    functions = []
    valid_count = 0
    
    for i, eq in enumerate(equations):
        if i % 100 == 0:
            print(f"处理方程 {i+1}/{len(equations)}...")
        
        try:
            func = create_function(eq)
            # 测试函数是否有效
            test_valid = False
            for test_x in range(0, matrix_size, 5):
                if not math.isinf(func(test_x)):
                    test_valid = True
                    break
            
            if test_valid:
                functions.append(func)
                valid_count += 1
        except:
            continue
    
    print(f"有效方程数量: {valid_count}/{len(equations)}")
    
    # 初始化矩阵
    C = np.zeros([matrix_size, matrix_size])
    
    # 将所有方程映射到矩阵并叠加
    print("映射方程到矩阵...")
    for i, func in enumerate(functions):
        if i % 50 == 0:
            print(f"映射进度: {i+1}/{len(functions)}")
        
        func_matrix = plus(func, matrix_size)
        C += func_matrix
    
    print(f"初始矩阵最大值: {np.max(C)}")
    print(f"初始矩阵非零元素: {np.count_nonzero(C)}")
    
    # 创建遗忘函数
    forget_func = create_forget_function(forget_curve_expr)
    
    # 遗忘过程
    print("开始遗忘过程...")
    for t in range(time_steps):
        if t % 10 == 0:
            print(f"遗忘步骤: {t+1}/{time_steps}, 矩阵最大值: {np.max(C):.4f}")
        
        # 计算遗忘量
        forget_amount = forget_func(t * 0.01) - forget_func((t + 1) * 0.01)
        C -= forget_amount
        
        # 确保矩阵值不为负
        C = np.maximum(C, 0)
    
    print(f"遗忘后矩阵最大值: {np.max(C)}")
    print(f"遗忘后矩阵非零元素: {np.count_nonzero(C)}")
    
    return C, valid_count

def find_solutions(matrix, noise_threshold):
    """从矩阵中找到解"""
    # 归一化矩阵
    if np.max(matrix) > 0:
        normalized_matrix = matrix / np.max(matrix)
    else:
        normalized_matrix = matrix
    
    # 寻找高值区域作为解
    threshold = noise_threshold / 100
    solutions = []
    
    for x in range(matrix_size):
        for y in range(matrix_size):
            if normalized_matrix[x][y] >= threshold:
                solutions.append((x, y, normalized_matrix[x][y]))
    
    # 按置信度排序
    solutions.sort(key=lambda s: s[2], reverse=True)
    
    return solutions

def calculate_solution_error(found_solutions, true_solutions):
    """计算求解误差"""
    if not found_solutions or not true_solutions:
        return float('inf'), float('inf'), 0
    
    # 对每个真实解，找到最近的计算解
    errors = []
    
    for true_x, true_y in true_solutions:
        min_distance = float('inf')
        
        for found_x, found_y, confidence in found_solutions[:20]:  # 只考虑前20个最可能的解
            distance = math.sqrt((found_x - true_x)**2 + (found_y - true_y)**2)
            min_distance = min(min_distance, distance)
        
        errors.append(min_distance)
    
    if errors:
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        solved_count = sum(1 for e in errors if e <= 2.0)  # 误差在2个单位内认为求解成功
        
        return avg_error, max_error, solved_count
    
    return float('inf'), float('inf'), 0

def main():
    print("=== 遗忘算法求解1000方程联立方程组 ===")
    print(f"参数设置:")
    print(f"遗忘百分比: {forget_percentage}×10%")
    print(f"矩阵大小: {matrix_size}×{matrix_size}")
    print(f"遗忘曲线: {forget_curve}")
    print(f"噪声水平: {noise_level}%")
    print("="*60)
    
    # 生成1000个方程
    equations, true_solutions = generate_solvable_1000_equations()
    print(f"生成了 {len(equations)} 个方程")
    print(f"预期解点: {true_solutions}")
    
    # 使用遗忘算法求解
    result_matrix, valid_equations = forget_algorithm_solve(
        equations, forget_curve, forget_percentage * 10, noise_level
    )
    
    # 寻找解
    found_solutions = find_solutions(result_matrix, noise_level)
    
    print(f"\n=== 求解结果 ===")
    print(f"找到 {len(found_solutions)} 个候选解")
    
    if found_solutions:
        print("前10个最可能的解:")
        for i, (x, y, confidence) in enumerate(found_solutions[:10]):
            print(f"解 {i+1}: ({x}, {y}) 置信度: {confidence:.4f}")
    
    # 计算误差
    avg_error, max_error, solved_count = calculate_solution_error(found_solutions, true_solutions)
    
    print(f"\n=== 误差分析 ===")
    print(f"有效方程数量: {valid_equations}/{len(equations)}")
    print(f"预期解数量: {len(true_solutions)}")
    print(f"找到解数量: {len(found_solutions)}")
    print(f"成功求解数量: {solved_count}/{len(true_solutions)}")
    
    if avg_error != float('inf'):
        print(f"平均位置误差: {avg_error:.4f} 个单位")
        print(f"最大位置误差: {max_error:.4f} 个单位")
        
        # 相对误差（相对于矩阵大小）
        relative_avg_error = avg_error / matrix_size
        relative_max_error = max_error / matrix_size
        
        print(f"平均相对误差: {relative_avg_error:.6f} ({relative_avg_error*100:.4f}%)")
        print(f"最大相对误差: {relative_max_error:.6f} ({relative_max_error*100:.4f}%)")
        
        # 求解成功率
        success_rate = solved_count / len(true_solutions)
        print(f"求解成功率: {success_rate:.2%}")
        
        # 精度评估
        if relative_avg_error < 0.02:
            precision_level = "高精度"
        elif relative_avg_error < 0.05:
            precision_level = "中等精度"
        elif relative_avg_error < 0.1:
            precision_level = "低精度但可用"
        else:
            precision_level = "精度不足"
        
        print(f"整体精度等级: {precision_level}")
        
        return {
            'valid_equations': valid_equations,
            'found_solutions': len(found_solutions),
            'solved_count': solved_count,
            'success_rate': success_rate,
            'average_error': avg_error,
            'relative_average_error': relative_avg_error,
            'precision_level': precision_level
        }
    else:
        print("求解失败")
        return None

if __name__ == "__main__":
    results = main()