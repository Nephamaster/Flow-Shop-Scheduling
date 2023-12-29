import matplotlib.pyplot as plt
from Intelligent_Search import *
from Instance_read import *

# 定义目标函数
# solution为某一调度时间表, 以numpy矩阵表示:
# solution[i, j] 代表第j个工件在第i个机器的加工完成时刻
def ObFunc(solution):
    maxtime = 0
    mac = solution.shape[0]
    # 机器中加工完成时刻的最大值即调度总时间
    for m in range(mac):
        if maxtime <= solution[m,-1]:
            maxtime = solution[m,-1]
    return maxtime

# 运行函数
def work(mode, C=100, R=5, T0=10000, Tt=0.01, yita=0.99):
    # mode 代表运行模式, 数据类型为字符串
    # mode == 'HC' 为登山搜索算法, mode == 'RS' 为轮盘赌-模拟退火算法
    # R, T0, Tt, yita 为轮盘赌-模拟退火算法所需参数; C 为 登山搜索算法所需参数
    total_time = 0 # 记录运行时间

    # 求解11个用例
    for t in range(1):
        print("+++++++++++++++++++++++++++++")
        print("Instance", t)
        workpiece = table['instance'+str(10)]['workpiece']
        machine = table['instance'+str(10)]['machine']
        instance = np.zeros((machine, workpiece))
        # 将用例信息存入 numpy 二维矩阵 instance
        # 矩阵行数为机器数machine, 列数为工件数workpiece
        for m in range(machine):
            for w in range(workpiece):
                instance[m, w] = table['instance'+str(10)]['wp'+str(w+1)][m]

        IS = None
        if mode == 'HC': # 登山搜索
            IS = Hill_Climb(function=ObFunc,
                            data=instance,
                            C=C)
            IS.climb()
        elif mode == 'RS': # 轮赌-模拟退火
            IS = Roulette_SA(function=ObFunc,
                             data=instance,
                             R=R, T0=T0, Tt=Tt, yita=yita)
            IS.anneal()

        '''# 生成时序图
        plt.style.use('ggplot')
        plt.title('Instance {}'.format(t))
        if mode == 'HC':
            times = np.arange(0, IS.times, 1)
            plt.plot(times, IS.V_history, color='lightcoral')
            plt.xlabel('Times')
        elif mode == 'RS':
            plt.plot(IS.T_history, IS.V_history, color='lightcoral')
            plt.xlabel('Temperature')
            plt.gca().invert_xaxis()
        plt.ylabel('Value')
        plt.show()'''

        # 打印结果
        print("Optimum Result:\nMin_Time =", int(IS.optimum['value']))
        print("Solution:")
        solution = IS.optimum['solution'].astype(int)
        # Processing Order 为机器加工工件顺序, 以列表形式输出
        print("Processing Order:", list(IS.order))
        # 以机器为基准打印调度方案
        for s in range(solution.shape[0]):
            print("Machine"+str(s+1), list(solution[s]))
        # 打印该用例运行时间
        print("Running Time:", IS.endtime - IS.startime, "s")
        total_time += IS.endtime - IS.startime # 总运行时增加

    print("+++++++++++++++++++++++++++++")
    # 打印总运行时间
    print("Total Running Time:", total_time, "s")

if __name__ == '__main__':
    # 登山搜索与轮赌-模拟退火分别求解，不想执行哪一个算法可以先注释掉
    # work(mode='HC', C=1000)
    work(mode='RS', R=1, T0=1000, Tt=1e-20, yita=0.99)