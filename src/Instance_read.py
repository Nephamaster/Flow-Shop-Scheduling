from copy import deepcopy

i = -1
table = {}
temp = {}

# 读取示例时删除每个工件时间前的序号
def del_num(machine):
    list = []
    for m in range(len(machine)):
        if m % 2 != 0:
            list.append(int(machine[m]))
    return list

# 读取示例
with open("Instance.txt", "r") as f:
    for line in f.read().splitlines():
        line = list(filter(None, line.split(' ')))
        # 将每一个示例存储到字典变量: { 工件数, 机器数, 工件-机器加工时间 }
        if line != ['+++++++++++++++++++++++++++++']:
            if line[0] == 'instance':
                i += 1
            elif line[0] != '0':
                # 存储工件数 workpiece 和机器数 machine
                temp['workpiece'] = wp = k = int(line[0])
                temp['machine'] = int(line[1])
            else:
                # 以工件为基准存储加工时间
                temp['wp'+str(k-wp+1)] = del_num(line)
                wp -= 1
                if wp == 0:
                    table['instance'+str(i)] = deepcopy(temp)
                    temp.clear()