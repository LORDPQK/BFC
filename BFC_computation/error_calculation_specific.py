()
    main:_"= "__main_name__ =f __")

i在噪声水平范围内int("✓ 计算误差         pr     else:
      ")
响结果精度能影于计算误差，可"⚠ 噪声水平高  print(         ve_error:
  max_relatiise_ratio >no  if    ")
   o:.2f}ratioise_{n比例: int(f"噪声pr      100
  evel / io = noise_lrat      noise_ 噪声影响分析
        #  
  ")
      nc(1):.4f} {forget_fu在t=1时的值:f"遗忘曲线     print(
   :.4f}")_func(0)rgetfo的值: {在t=0时f"遗忘曲线int(        prcurve)
orget_on(fcti create_funnc =get_fuor   f析遗忘曲线
           # 分   
      ")
 entage}_percforget {遗忘时间步数:rint(f"  p    :")
  定分析\n遗忘算法特"print(f     
    遗忘算法特定分析        #   

     前误差较大")议增大矩阵大小，当"⚠ 强烈建rint(     p  :
      else
       高精度")大矩阵大小以提建议增print("⚠       05:
      < 0.ve_error relativg_f a      eli可接受")
  小合适，误差阵大✓ 当前矩rint("           pr < 0.01:
 elative_erro avg_r  elif")
      小差极大小足够，误nt("✓ 当前矩阵pri            0.001:
 tive_error < avg_relaif")
        统建议:nt(f"\n系ri
        p  # 系统建议      
  )
      .4f}%)"rror*100:ive_eelatax_rror:.6f} ({mative_er差: {max_rel(f"最大相对误 print     )")
  00:.4f}%*1tive_erroravg_relaf} ({r:.6_erroative{avg_rel"平均相对误差: rint(f    p
       )
     l_errorsr e in totarror'] fove_ee['relatiax(ror = mative_erx_relma        
otal_errors) len(trors) /in total_ere for ] tive_error'um(e['rela sive_error =relat        avg_
s: total_error   if 
    ")
总体误差分析:t("in*50)
    pr" + "="int(f"\n分析
    pr
    # 总体误差})
    
        ityomplexplexity': c     'com
       rror,interp_eror': ion_eratinterpol           '
 el_error,error': r 'relative_          
 or,ms_errrror': rrms_e           'str,
 uation': eq_    'eq{
        s.append(otal_error    t
    )
        误差<1%)"目标相对ted_size} (ggesize}×{suted_s {sugges阵大小:(f"建议矩print          1))
  error / 0.0(rel_math.sqrtix_size * nt(matr= iize ted_sges sug         01:
  ror > 0.el_er    if r  
  # 精度建议        
      ")
  rror_level}"误差等级: {e print(f  
             高"
l = "r_leve        erro      else:
"
      "中等evel = or_l         err   or < 0.05:
f rel_err
        eli低" "l =_leve  error       0.01:
   ror < elif rel_er"
        极低_level = "or        err01:
    < 0.0 rel_error  if       评估
       # 误差     
 .6f}")
   lexity: (曲率): {comp"函数复杂度print(f)
        _sizeunc, matrixexity(fplunction_comnalyze_fty = axi comple    函数复杂度
   
        #  )
       }"rror:.6finterp_e(RMS): {f"插值误差 rint()
        pix_sizetrmar(func, rrotion_ee_interpola calculat_error =    interp误差
     # 插值 
          
    4f}%)")ror*100:.{rel_er.6f} (_error:"相对误差: {rel    print(fze)
    x_simatrir(func, rotive_erulate_relacalc=  rel_error 
           # 相对误差
     )
       }"n_error:.6f  平均误差: {mea(f"   print
     6f}")error:. {max_t(f"  最大误差:rin p  
     }")rror:.6f误差: {rms_ent(f"  RMSpri      化误差:")
  (f"量print)
        size, matrix_r(func_errotionizalate_quantcu = calean_errorx_error, mmams_error,         r误差
# 量化         
    0)
   " * 3 print("-)
       q_str}"{e y = 1}:"\n方程 {i+t(f    prins):
    unction enumerate(f func) ineq_str,i, (
    for 
    []al_errors = 
    tot分析每个函数的误差 # 
   )
    eq}': {e}" '{警告: 无法解析方程  print(f"      e:
     Exception as    except ))
    , funceqend((unctions.app         f
   ion(eq)reate_functc = c       fun  y:
    tr   tions:
    qua e ineq    for ns = []
ctio
    fun函数对象  # 创建)
    
  "="*50+ "\n" nt(   privel}")
 ise_le: {no"噪声水平    print(f")
_curve}曲线: {forgetrint(f"遗忘
    pe}×10%")ercentag: {forget_p分比t(f"遗忘百)
    prinsize}"x_e}×{matritrix_siz"矩阵大小: {ma
    print(fons}")uati"方程组: {eq    print(f入参数:")
  print(f"输=")
  算法离散化误差分析 =="=== 遗忘
    print(main():
def 0
urn ret        pt:
    exceature
urn avg_curv rets)
       curvatureures) / len(curvat = sum(urvature    avg_c  
          eturn 0
         r) == 0:
   atures len(curv
        if      ue
    contin             pt:
 ce  ex         
 ve))ivati(second_derd(absatures.appen       curv  
       r + y_prev*y_cur 2t -e = y_nexnd_derivativ    seco            近似二阶导数
 # 二阶差分                   
 
           n(x + 1)nctionext = fu  y_   
           ion(x)= funct_curr  y           1)
    on(x -  functi y_prev =        y:
               tr  1):
  ize -  matrix_se(1,r x in rang      fo  = []
 curvatures       的近似值来评估曲率
 导数 # 计算二阶
       
    try:复杂度"""分析函数 """e):
   izx_sn, matri(functio_complexitynctionyze_fual))

def anerrors) / len(n errors ifor em(e*e math.sqrt(surn     return 0
    
     retu   ors) == 0:
 if len(err
   e
      continu       pt:
        excer)
   rros.append(e  error          )
    terp- y_inbs(y_real ror = a      er    
                 y0)
      (y1 - y0 + t *erp =       y_int        n(x + 1)
   functio      y1 =        
   function(x)      y0 =
          插值值线性#              
                 _sample)
  on(xncti = fuy_real            
     + tle = xmp_sa          x.9]:
      0.8, 00.7, 6, .4, 0.5, 0..2, 0.3, 0.1, 0in [0   for t          采样
, x+1]区间进行     # 在[x
             try:):
  - 1x_size e(matri x in rang for
    
   = [] errors "
   算插值误差"""计  ""
  x_size):atrin, mnction_error(fuolatioate_interpdef calcul

eturn 0
        r:exceptror
    relative_erurn         ret_range
error / yrror = rms_ive_e      relat)
  atrix_sizection, mfun_error(quantizationte_ = calcula _, _r,    rms_erro  
    0
      turn       re   :
   e == 0f y_rang      i 
        lues)
 min(y_vay_values) - ge = max(ran y_ 
               eturn 0
     r          = 0:
(y_values) =      if len
          inue
  cont             xcept:
       e      
ction(x))d(fun.appen   y_values         ry:
          t      ix_size):
n range(matr for x i      ues = []
     y_val  
  try:    差"""
"计算相对误):
    ""_size, matrixnction_error(futivee_reladef calculat_error

or, meanror, max_err_ereturn rms   
    rrs)
  / len(erroum(errors)error = s   mean_)
 rrors= max(eor  max_err
   len(errors))ors) /  in errfor eqrt(sum(e*e or = math.s   rms_err
    
 n 0, 0, 0turre    == 0:
    ) n(errors if le      
d(0)
 rrors.appen      e  误
    理可能的计算错  # 处
          ept:xc        ed(error)
penaprrors.       e  screte)
   _real - y_di= abs(y   error         # 四舍五入到整数
 ) al + 0.5t(y_re = in  y_discrete     
       # 真实函数值)          function(xl =_rea   y  ry:
             t_size):
  ge(matrixx in ran  for   rs = []
rro   e
 """误差  """计算量化x_size):
  on, matrirror(functiion_etizatate_quancul

def caleturn f    r
x', str(x)))lace('', '**').repeplace('^on.rpressieval(exreturn         ef f(x):
  d"""
  函数为计算机表达式转换"将文本""
    :ession)on(exprctiunreate_f水平

def c= 10  # 噪声oise_level 曲线方程
n # 遗忘-x/0.23)" 2.71828^(.2*urve = "6orget_c矩阵大小
fe = 64  # 遗忘
matrix_siz*10%）比（忘百分age = 5  # 遗ntpercet_y=1
forge2 和 y=x*, "1"]  # ["x*2"ions = 数据
equatnp

# 输入 numpy as port
imimport math