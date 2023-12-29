from random import random, sample
import time as tm
import numpy as np

# 贪心生成初始加工时间表, data 为用例调度信息
def greed_initial(data):
    # 定义工件加工时间表
    solution = np.zeros((data.shape[0], data.shape[1]))
    # 按加工绝对时长由大到小安排调度; 从0时刻开始, 尽量紧密安排
    time = 0
    arranged = []
    for m in range(solution.shape[0]):
        # 时间表第 w 项记录第 w 个工件在第 m 个机器加工完成时刻
        for w in range(solution.shape[1]):
            # 避免一个工件同时在多个机器加工
            for a in range(len(arranged)):
                if time < solution[arranged[a], w]:
                    time = solution[arranged[a], w]
            time += data[m, w]
            solution[m, w] = time
        # time置为当前机器给第一个工件加工的完成时刻, 作为下一个机器加工开始时刻
        time = solution[m, 0]
        arranged.append(m)  # 将已安排过的机器存入列表

    return solution

# 随机产生新方案
def random_generate(Order, data, current):
    # 输入说明:
    # Order 为当前加工顺序表, data为用例调度信息, current 为当前加工时间表
    machine = current.shape[0]
    workpiece = current.shape[1]
    new = current.copy()
    order = Order.copy()
    # 随机选取两个个工件, 交换其加工顺序
    rand = sample(range(0, workpiece), 2)
    t1 = order[rand[0]]
    t2 = order[rand[1]]
    order[rand[0]] = t2
    order[rand[1]] = t1
    # 根据交换后的加工顺序表, 安排调度
    arranged = []
    time = 0
    for m in range(machine):
        for w in range(workpiece):
            wk = order[w]
            # 避免一个工件同时在多个机器加工
            for a in range(len(arranged)):
                if time < new[arranged[a], w]:
                    time = new[arranged[a], w]
            time += data[m, wk]
            new[m, w] = time
        # time置为当前机器给第一个工件加工的完成时刻, 作为下一个机器加工开始时刻
        time = new[m, 0]
        arranged.append(m)
    # 输出新方案即 加工时间表 new, 加工顺序表 order
    return new, order

# 轮盘赌选择法
def roulette(scheme, obfunc):
    # 输入说明: scheme为一个字典变量, key-value: m-(new, order)
    # m 为新产生的方案数, new 为新调度时间表, order 为机器加工工件顺序
    # obfunc 为目标函数
    M = len(scheme)
    # f 为方案适应度, q 为方案累积概率, c为方案选中次数
    f, q, c = np.zeros(M), np.zeros(M), np.zeros(M)
    # 计算每个方案适应度, 将方案的目标函数值进行标准化处理, 增添负号后指数化作为适应度
    for m in range(M):
        f[m] = obfunc(scheme[m][0])
    minf = np.min(f)
    maxf = np.max(f)
    f = minf + maxf - f
    # 计算每个方案个体概率
    P = f / np.sum(f)
    # 计算每个方案累积概率
    for m in range(M):
        q[m] = np.sum(P[0:m])
    # 轮盘选择M次
    for m in range(M):
        r = random()
        for m1 in range(M):
            if r <= q[m1]:
                c[m1] += 1
                break
    # 选中次数最多的方案即 new 加工时间表和 order 加工顺序表作为输出
    return scheme[np.argmax(c)]

# 登山搜索算法
class Hill_Climb:
    def __init__(self, C, function, data):
        self.obfunc = function  # 目标函数
        self.data = data  # 调度初始信息矩阵
        self.order = np.arange(0, self.data.shape[1], 1)  # 加工顺序表
        self.C = C  # 选择新方案数
        # 最佳方案
        self.optimum = {'value': 0,  # 最优值
                        'solution': np.zeros((self.data.shape[0], self.data.shape[1]))  # 最优方案
                        }
        self.V_history = []  # 过程值记录
        self.times = 0  # 迭代次数记录

    # 登山搜索
    def climb(self):
        self.startime = tm.time()  # 开始计时
        # 生成初始方案
        scheme = greed_initial(self.data)
        result = self.obfunc(scheme)
        print("Initial_Time:", int(result))

        # 温度达到最小值时停止循环
        while True:
            # 产生 C 个新方案, 选取最优邻域解
            success_order, success_scheme, success_result = None, None, 100000
            for r in range(self.C):
                new, order = random_generate(self.order, self.data, scheme)
                new_result = self.obfunc(new)
                # 更新邻域最优解
                if new_result < success_result:
                    success_order = order
                    success_result = new_result
                    success_scheme = new
            # 贪心接受新解
            if success_result < result:
                scheme = success_scheme.copy()
                result = success_result
                self.order = success_order
                self.V_history.append(result)  # 记录过程值
                self.times += 1 # 迭代次数加一
            # 或收敛于局部最优解
            else:
                self.optimum['value'] = result
                self.optimum['solution'] = scheme.copy()
                self.endtime = tm.time()  # 结束计时
                break

# 轮盘赌-模拟退火算法
class Roulette_SA:
    def __init__(self, function, data, R=5, T0=10000, Tt=0.01, yita=0.95):
        # 冷却进度表
        self.cool_schedule = {'T0': T0,  # 初始温度, default = 10000
                              'Tt': Tt,  # 最终温度, default = 0.01
                              'yita': yita  # 降温系数, default = 0.95
                              }
        self.R = R  # 轮盘赌产生方案数, default = 5
        self.T = T0  # 当前温度T, 初始等于T0
        self.obfunc = function  # 目标函数, 作为能量
        self.data = data  # 调度初始信息矩阵
        self.order = np.arange(0, self.data.shape[1], 1)  # 加工顺序表
        # 最佳方案
        self.optimum = {'value': 0,  # 最优值
                        'solution': np.zeros((self.data.shape[0], self.data.shape[1]))  # 最优方案
                        }
        self.T_history = []  # 温度记录
        self.V_history = []  # 结果记录

    # 接受新方案
    def accept_new(self, E_new, E):
        delta = E_new - E  # 能量增量
        if delta <= 0:
            return 1
        else:
            # Metropolis准则
            p = np.exp(-delta / self.T)
            if random() < p:
                return 1
            else:
                return 0

    # 模拟退火
    def anneal(self):
        self.startime = tm.time()  # 开始计时
        # 生成初始方案
        current = greed_initial(self.data)
        result = self.obfunc(current)
        print("Initial_Time:", int(result))

        # 温度达到最小值时停止循环
        while self.T >= self.cool_schedule['Tt']:
            self.T_history.append(self.T)
            # 轮盘赌选择法
            scheme = {}
            # 产生 R 个新方案
            for r in range(self.R):
                new, order = random_generate(self.order, self.data, current)
                scheme[r] = (new, order)
            new, order = roulette(scheme, self.obfunc)
            result_new = self.obfunc(new)
            # 选择是否接受新解
            if self.accept_new(result_new, result):
                current = new.copy()
                result = result_new
                self.order = order

            self.V_history.append(result) # 记录过程值
            self.T *= self.cool_schedule['yita']  # 降温

        # 收敛到最优解
        self.optimum['value'] = result
        self.optimum['solution'] = current.copy()
        self.endtime = tm.time()  # 结束计时