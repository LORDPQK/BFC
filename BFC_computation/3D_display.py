import numpy as np
import pyvista as pv
import time
from vtk import vtkCommand  # 导入VTK事件类型

# 向量化坐标变换和旋转函数
def galilean_transformation(x, large):
    return (x - 0.5 * large) / 10

def rotate_point_3d_vectorized(x, y, z, angle_x, angle_y, angle_z):
    cos_x, sin_x = np.cos(angle_x), np.sin(angle_x)
    cos_y, sin_y = np.cos(angle_y), np.sin(angle_y)
    cos_z, sin_z = np.cos(angle_z), np.sin(angle_z)
    
    # X轴旋转
    y_new = y * cos_x - z * sin_x
    z_new = y * sin_x + z * cos_x
    
    # Y轴旋转
    x_rot = x * cos_y + z_new * sin_y
    z_rot = -x * sin_y + z_new * cos_y
    
    # Z轴旋转
    x_final = x_rot * cos_z - y_new * sin_z
    y_final = x_rot * sin_z + y_new * cos_z
    
    return x_final, y_final, z_rot

# 生成初始三维矩阵（缩小规模以提升性能）
large = 80
i, j, k = np.indices((large, large, large))
C = np.zeros((large, large, large))

functionList = [
    (3, 3, 3, -1.5, 0, 0, np.pi/6, 0, 0),
    (3, 3, 3, 1.5, 0, 0, 0, np.pi/6, 0)
]

for params in functionList:
    a, b, c, x0, y0, z0, angle_x, angle_y, angle_z = params
    x = galilean_transformation(i, large)
    y = galilean_transformation(j, large)
    z = galilean_transformation(k, large)
    
    x_rot, y_rot, z_rot = rotate_point_3d_vectorized(x, y, z, 
                                                     angle_x, angle_y, angle_z)
    
    mask = ((x_rot - x0)**2/a**2 + 
           (y_rot - y0)**2/b**2 + 
           (z_rot - z0)**2/c**2 <= 1)
    C[mask] += 1

C = np.clip(C - 0.5, 0, None)


# 创建可视化器
pl = pv.Plotter()

# 创建初始点云
points = np.argwhere(C > 0).astype(np.float32)
values = C[points[:,0].astype(int), points[:,1].astype(int), points[:,2].astype(int)]
point_cloud = pv.PolyData(points, force_float=False)
point_cloud['values'] = values

# 增强颜色对比度
cmap = pv.LookupTable()
cmap.value_range = (0, 1.0)
cmap.hue_range = (0.7, 0.9)
cmap.saturation_range = (0.8, 1.0)
cmap.alpha_range = (0.7, 0.3)

# 创建可视化器
pl = pv.Plotter()
actor = pl.add_mesh(point_cloud, scalars='values', cmap=cmap,
                   point_size=20, render_points_as_spheres=True)
pl.background_color = 'white'

# 动态参数
last_update = time.time()
update_interval = 1  # 更新间隔0.5秒
decay_rate = 0.3

# 修正回调函数参数（需接受VTK对象和事件参数）
def timer_callback(obj, event):
    print("Timer event triggered")
    global last_update, C, actor
    current_time = time.time()
    
    if current_time - last_update < update_interval:
        return
    
    # 执行衰减和更新点云（同之前代码）
    C = np.clip(C - decay_rate, 0, None)
    print(f"更新时间: {current_time:.1f}, 最大值: {np.max(C):.2f}")
    
    valid_points = C > 0
    if np.any(valid_points):
        points = np.argwhere(valid_points).astype(np.float32)
        values = C[valid_points]
        new_cloud = pv.PolyData(points, force_float=False)
        new_cloud['values'] = values
        pl.remove_actor(actor)
        actor = pl.add_mesh(new_cloud, scalars='values', cmap=cmap,
                          point_size=20, render_points_as_spheres=True)
    else:
        pl.remove_actor(actor)
        actor = None
    
    last_update = current_time
    pl.update()

# 使用VTK原生方法绑定定时器（关键修正！）
pl.iren.add_observer(vtkCommand.TimerEvent, timer_callback)  # 使用事件对象而非字符串
timer_id = pl.iren.create_timer(100)  # 100毫秒触发检查，实际更新由update_interval控制

pl.show()