# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 14:53:57 2023

@author: duyaya
"""


# 定义内存分区类
class Partition:
    def __init__(self, start, size, state, process):
        self.start = start  # 起始地址
        self.size = size  # 大小
        self.state = state  # 状态，"free"或"allocated"
        self.process = process  # 占用的进程，None表示空闲
        self.next = None
        self.prev = None

    def __str__(self):
        return f"[{self.start}, {self.size}, {self.state}, {self.process}]"


# 定义内存分区链表类
class PartitionList:
    def __init__(self):
        self.head = None  # 头结点
        self.tail = None  # 尾结点
        self.length = 0  # 长度

    def append(self, partition):
        # 在链表尾部添加一个空闲分区
        if self.head is None:
            self.head = partition
            self.tail = partition
        else:
            self.tail.next = partition
            partition.prev = self.tail
            self.tail = partition
        self.length += 1

    def remove(self, partition):
        # 从链表中删除一个空闲分区
        if self.head is None:
            raise ValueError("List is empty")
        if self.head == partition:
            # 删除头结点
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            else:
                self.head.prev = None
        elif self.tail == partition:
            # 删除尾结点
            self.tail = self.tail.prev
            self.tail.next = None
        else:
            # 删除中间结点
            partition.prev.next = partition.next
            partition.next.prev = partition.prev
        self.length -= 1

    def sort_by_size(self):
        # 按照空闲分区的大小升序排序
        if self.length <= 1:
            return
        # 使用插入排序
        current = self.head.next
        while current is not None:
            temp = current
            current = current.next
            prev = temp.prev
            while prev is not None and prev.size > temp.size:
                prev = prev.prev
            self.remove(temp)
            if prev is None:
                self.insert(temp, 0)
                temp.prev = None  # 头指针的前一个为0
            else:
                self.insert(temp, self.index_of(prev) + 1)

    def insert(self, partition, index):
        # 在链表指定位置插入一个空闲分区
        if index < 0 or index > self.length:
            raise IndexError("Index out of range")
        if index == 0:
            # 在头部插入
            if self.head is None:
                self.head = partition
                self.tail = partition
            else:
                self.head.prev = partition
                partition.next = self.head
                self.head = partition
            self.length += 1
        elif index == self.length:
            # 在尾部插入
            self.append(partition)
        else:
            # 在中间插入
            current = self.head
            for i in range(index):
                current = current.next
            current.prev.next = partition
            partition.prev = current.prev
            partition.next = current
            current.prev = partition
            self.length += 1

    def index_of(self, partition):
        # 返回空闲分区在链表中的位置
        current = self.head
        index = 0
        while current is not None:
            if current == partition:
                return index
            current = current.next
            index += 1
        return -1

    def __str__(self):
        # 返回链表的字符串表示
        result = "["
        current = self.head
        while current is not None:
            result += str(current)
            if current.next is not None:
                result += ", "
            current = current.next
        result += "]"
        return result


# 定义进程类
class Process:
    def __init__(self, name, size):
        self.name = name  # 进程名
        self.size = size  # 进程大小

    def __str__(self):
        return self.name


# 定义内存回收算法
def memory_recycle(memory, Allocated_Memory, process):
    # 参数：memory是一个空闲分区链表，process是一个进程对象
    # 返回值：如果回收成功，返回一个回收后的空闲分区链表，否则返回None
    current = Allocated_Memory.head  # 定义一个当前结点，从头结点开始查找
    while current is not None:
        if current.process == process:  # 如果当前分区的进程是要回收的进程
            temp = memory.head
            index = current.start + current.size
            while temp is not None:
                if temp.start == index:  # 找到与释放内存相邻的内存块
                    temp.start = current.start
                    temp.size = current.size + temp.size
                    Allocated_Memory.remove(current)
                    return memory
                temp = temp.next
            temp2 = Partition(current.start, current.size, 'free', None)  # 没找到相邻内存块就直接加入
            memory.append(temp2)
            Allocated_Memory.remove(current)
            return memory
        current = current.next  # 继续查找下一个分区
    return None  # 如果没有找到要回收的进程，回收失败


# 内存分配函数
def allocate(flag, memory, Allocated_Memory, process):
    if flag == 1:
        temp = first_fit(memory, Allocated_Memory, process)
        if temp is None:
            print('分配失败')
        else:
            return temp
    elif flag == 2:
        temp = next_fit(memory, Allocated_Memory, process)
        if temp is None:
            print('分配失败')
        else:
            return temp
    elif flag == 3:
        temp = best_fit(memory, Allocated_Memory, process)
        if temp is None:
            print('分配失败')
        else:
            return temp
    else:
        temp = worst_fit(memory, Allocated_Memory, process)
        if temp is None:
            print('分配失败')
        else:
            return temp


# 首次适应算法
def first_fit(memory, Allocated_Memory, process):
    # 参数：memory是一个空闲分区链表，process是一个进程对象
    # 返回值：如果分配成功，返回一个分配后的空闲分区链表，否则返回None
    current = memory.head
    if current is None:
        print("List is empty")
        return None

    while True:
        if current.size >= process.size:
            # 如果当前空闲分区的大小能满足进程的需求
            if current.size == process.size:
                # 如果恰好相等，直接分配给进程，修改状态和进程属性，从链表中删除该空闲分区
                temp = Partition(current.start, current.size, "allocated", process)
                Allocated_Memory.append(temp)
                memory.remove(current)
            else:
                # 如果稍大一些，分割出一部分，修改状态和进程属性，更新空闲分区的起始地址和大小
                # 添加到已分配分区
                new_partition = Partition(current.start, process.size, "allocated", process)
                Allocated_Memory.append(new_partition)
                # 更新空闲分区
                new_start = current.start + process.size
                new_size = current.size - process.size
                current.start = new_start
                current.size = new_size
            return memory  # 返回分配后的空闲分区链表
        current = current.next  # 继续查找下一个空闲分区
        if current is None:
            return None


# 定义循环首次适应算法
def next_fit(memory, Allocated_Memory, process):
    # 参数：memory是一个空闲分区链表，process是一个进程对象
    # 返回值：如果分配成功，返回一个分配后的空闲分区链表，否则返回None
    global last  # 定义一个全局变量，记录上次分配的空闲分区
    if last is None:
        # 如果是第一次分配，从头结点开始查找
        last = memory.head
    current = last  # 定义一个当前结点，从上次分配的空闲分区的下一个分区开始查找
    while True:
        if current.size >= process.size:
            # 如果当前空闲分区的大小能满足进程的需求
            if current.size == process.size:
                # 如果恰好相等，直接分配给进程，修改状态和进程属性，从链表中删除该空闲分区
                temp = Partition(current.start, current.size, "allocated", process)
                Allocated_Memory.append(temp)
                last = current.next  # 更新全局变量last
                memory.remove(current)
            else:
                new_partition = Partition(current.start, process.size, "allocated", process)
                Allocated_Memory.append(new_partition)
                # 更新空闲分区
                new_start = current.start + process.size
                new_size = current.size - process.size
                current.start = new_start
                current.size = new_size
                last = current  # 更新全局变量last

            return memory  # 返回分配后的空闲分区链表
        current = current.next  # 继续查找下一个空闲分区
        if current is None:
            # 如果到达链表尾部，从头结点开始循环查找
            current = memory.head
        if current == last:
            # 如果回到起点，说明没有找到合适的空闲分区，分配失败
            return None


# 定义最佳适应算法
def best_fit(memory, Allocated_Memory, process):
    # 参数：memory是一个空闲分区链表，process是一个进程对象
    # 返回值：如果分配成功，返回一个分配后的空闲分区链表，否则返回None
    memory.sort_by_size()  # 按照空闲分区的大小升序排序

    current = memory.head  # 定义一个当前结点，从头结点开始查找
    while current is not None:
        if current.size >= process.size:  # 如果当前空闲分区的大小能满足进程的需求
            # 如果当前空闲分区的大小能满足进程的需求
            if current.size == process.size:
                # 如果恰好相等，直接分配给进程，修改状态和进程属性，从链表中删除该空闲分区
                temp = Partition(current.start, current.size, "allocated", process)
                Allocated_Memory.append(temp)
                memory.remove(current)
            else:
                # 如果稍大一些，分割出一部分，修改状态和进程属性，更新空闲分区的起始地址和大小
                # 添加到已分配分区
                new_partition = Partition(current.start, process.size, "allocated", process)
                Allocated_Memory.append(new_partition)
                # 更新空闲分区
                new_start = current.start + process.size
                new_size = current.size - process.size
                current.start = new_start
                current.size = new_size
            return memory  # 返回分配后的空闲分区链表

        current = current.next  # 继续查找下一个空闲分区

    return None  # 如果没有找到合适的空闲分区，分配失败


# 定义最差适应算法
def worst_fit(memory, Allocated_Memory, process):
    # 参数：memory是一个空闲分区链表，process是一个进程对象
    # 返回值：如果分配成功，返回一个分配后的空闲分区链表，否则返回None
    memory.sort_by_size()  # 按照空闲分区的大小升序排序
    current = memory.tail  # 定义一个当前结点，从尾结点开始查找
    while current is not None:
        if current.size >= process.size:  # 如果当前空闲分区的大小能满足进程的需求
            # 如果当前空闲分区的大小能满足进程的需求
            if current.size == process.size:
                # 如果恰好相等，直接分配给进程，修改状态和进程属性，从链表中删除该空闲分区
                temp = Partition(current.start, current.size, "allocated", process)
                Allocated_Memory.append(temp)
                memory.remove(current)
            else:
                # 如果稍大一些，分割出一部分，修改状态和进程属性，更新空闲分区的起始地址和大小
                # 添加到已分配分区
                new_partition = Partition(current.start, process.size, "allocated", process)
                Allocated_Memory.append(new_partition)
                # 更新空闲分区
                new_start = current.start + process.size
                new_size = current.size - process.size
                current.start = new_start
                current.size = new_size
            return memory  # 返回分配后的空闲分区链表
        current = current.prev  # 继续查找上一个空闲分区
    return None  # 如果没有找到合适的空闲分区，分配失败


def test1(memory, Allocated_Memory, P):
    # 测试首次适应算法
    print("1、测试首次适应算法")
    print("初始内存空间：", memory)
    allocate(1, memory, Allocated_Memory, P[0])
    print("分配进程P1后的内存空间：", memory)
    print("分配进程P1后的分配空间：", Allocated_Memory)
    allocate(1, memory, Allocated_Memory, P[1])
    print("分配进程P2后的内存空间：", memory)
    print("分配进程P2后的分配空间：", Allocated_Memory)
    allocate(1, memory, Allocated_Memory, P[2])
    print("分配进程P3后的内存空间：", memory)
    print("分配进程P3后的分配空间：", Allocated_Memory)
    allocate(1, memory, Allocated_Memory, P[3])
    print("分配进程P4后的内存空间：", memory)
    print("分配进程P4后的分配空间：", Allocated_Memory)
    allocate(1, memory, Allocated_Memory, P[4])
    print("分配进程P5后的内存空间：", memory)
    print("分配进程P5后的分配空间：", Allocated_Memory)

    print('回收进程空间')
    memory = memory_recycle(memory, Allocated_Memory, P[1])  # 回收进程P1
    print("回收进程P2后的内存空间：", memory)
    print("回收进程P2后的分配空间：", Allocated_Memory)
    memory = memory_recycle(memory, Allocated_Memory, P[0])  # 回收进程P1
    print("回收进程P1后的内存空间：", memory)
    print("回收进程P1后的分配空间：", Allocated_Memory)


def test2(memory, Allocated_Memory, P):
    # 测试循环首次适应算法
    print("2、测试循环首次适应算法")
    print("初始内存空间：", memory)
    allocate(2, memory, Allocated_Memory, P[0])
    print("分配进程P1后的内存空间：", memory)
    print("分配进程P1后的分配空间：", Allocated_Memory)
    allocate(2, memory, Allocated_Memory, P[1])
    print("分配进程P2后的内存空间：", memory)
    print("分配进程P2后的分配空间：", Allocated_Memory)
    allocate(2, memory, Allocated_Memory, P[2])
    print("分配进程P3后的内存空间：", memory)
    print("分配进程P3后的分配空间：", Allocated_Memory)
    allocate(2, memory, Allocated_Memory, P[3])
    print("分配进程P4后的内存空间：", memory)
    print("分配进程P4后的分配空间：", Allocated_Memory)
    allocate(2, memory, Allocated_Memory, P[4])
    print("分配进程P5后的内存空间：", memory)
    print("分配进程P5后的分配空间：", Allocated_Memory)

    print('回收进程空间')
    memory = memory_recycle(memory, Allocated_Memory, P[1])  # 回收进程P1
    print("回收进程P2后的内存空间：", memory)
    print("回收进程P2后的分配空间：", Allocated_Memory)
    memory = memory_recycle(memory, Allocated_Memory, P[0])  # 回收进程P1
    print("回收进程P1后的内存空间：", memory)
    print("回收进程P1后的分配空间：", Allocated_Memory)


def test3(memory, Allocated_Memory, P):
    # 测试循环首次适应算法
    print("3、测试最佳适应算法")
    print("初始内存空间：", memory)
    allocate(3, memory, Allocated_Memory, P[0])
    print("分配进程P1后的内存空间：", memory)
    print("分配进程P1后的分配空间：", Allocated_Memory)
    allocate(3, memory, Allocated_Memory, P[1])
    print("分配进程P2后的内存空间：", memory)
    print("分配进程P2后的分配空间：", Allocated_Memory)
    allocate(3, memory, Allocated_Memory, P[2])
    print("分配进程P3后的内存空间：", memory)
    print("分配进程P3后的分配空间：", Allocated_Memory)
    allocate(3, memory, Allocated_Memory, P[3])
    print("分配进程P4后的内存空间：", memory)
    print("分配进程P4后的分配空间：", Allocated_Memory)
    allocate(3, memory, Allocated_Memory, P[4])
    print("分配进程P5后的内存空间：", memory)
    print("分配进程P5后的分配空间：", Allocated_Memory)

    print('回收进程空间')
    memory = memory_recycle(memory, Allocated_Memory, P[1])  # 回收进程P1
    print("回收进程P2后的内存空间：", memory)
    print("回收进程P2后的分配空间：", Allocated_Memory)
    memory = memory_recycle(memory, Allocated_Memory, P[0])  # 回收进程P1
    print("回收进程P1后的内存空间：", memory)
    print("回收进程P1后的分配空间：", Allocated_Memory)


def test4(memory, Allocated_Memory, P):
    # 测试循环首次适应算法
    print("4、测试最差适应算法")
    print("初始内存空间：", memory)
    allocate(4, memory, Allocated_Memory, P[0])
    print("分配进程P1后的内存空间：", memory)
    print("分配进程P1后的分配空间：", Allocated_Memory)
    allocate(4, memory, Allocated_Memory, P[1])
    print("分配进程P2后的内存空间：", memory)
    print("分配进程P2后的分配空间：", Allocated_Memory)
    allocate(4, memory, Allocated_Memory, P[2])
    print("分配进程P3后的内存空间：", memory)
    print("分配进程P3后的分配空间：", Allocated_Memory)
    allocate(4, memory, Allocated_Memory, P[3])
    print("分配进程P4后的内存空间：", memory)
    print("分配进程P4后的分配空间：", Allocated_Memory)
    allocate(4, memory, Allocated_Memory, P[4])
    print("分配进程P5后的内存空间：", memory)
    print("分配进程P5后的分配空间：", Allocated_Memory)

    print('回收进程空间')
    memory = memory_recycle(memory, Allocated_Memory, P[1])  # 回收进程P1
    print("回收进程P2后的内存空间：", memory)
    print("回收进程P2后的分配空间：", Allocated_Memory)
    memory = memory_recycle(memory, Allocated_Memory, P[0])  # 回收进程P1
    print("回收进程P1后的内存空间：", memory)
    print("回收进程P1后的分配空间：", Allocated_Memory)


# 定义一个初始内存空间，共有5个分区，大小分别为130, 70, 140, 80, 20
memory = PartitionList()  # 创建一个空闲分区链表
memory.append(Partition(0, 130, "free", None))  # 添加第一个空闲分区
memory.append(Partition(130, 70, "free", None))  # 添加第二个空闲分区
memory.append(Partition(200, 140, "free", None))  # 添加第三个空闲分区
memory.append(Partition(340, 80, "free", None))  # 添加第四个空闲分区
memory.append(Partition(420, 20, "free", None))  # 添加第五个空闲分区

# 定义一个已被分配内存的链表
Allocated_Memory = PartitionList()

# 定义一些测试用的进程
p1 = Process("P1", 50)  # 进程P1，大小为50
p2 = Process("P2", 60)  # 进程P2，大小为60
p3 = Process("P3", 40)  # 进程P3，大小为40
p4 = Process("P4", 30)  # 进程P4，大小为30
p5 = Process("P5", 20)  # 进程P5，大小为20

# 定义一个全局变量，记录上次分配的空闲分区
last = None
# 定义进程集合
P = [p1, p2, p3, p4, p5]

# test1(memory, Allocated_Memory, P) # 测试首次适应分配
# test2(memory, Allocated_Memory, P) # 测试循环首次适应分配
# test3(memory, Allocated_Memory, P) # 测试最佳适应分配
test4(memory, Allocated_Memory, P)  # 测试最差适应分配
