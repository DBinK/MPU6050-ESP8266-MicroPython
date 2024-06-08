

def window_filter(value, values, window_size=50):
    # 将值添加到列表中
    values.append(value)

    # 如果列表长度超过窗口大小，则移除最旧的元素
    if len(values) > window_size:
        values.pop(0)

    # 返回平均值
    return sum(values) / len(values)