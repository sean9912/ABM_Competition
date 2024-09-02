import solara
import numpy as np
from model import TSAE
from Agents import Owners, Consumers, Platform
import time
import pandas as pd

# 初始化模型
model = TSAE()

# 记录循环开始时间
start_time = time.time()

# 初始化一个空 DataFrame，用于存储所有模型运行的结果
all_results = pd.DataFrame()


@solara.component
def render_model():
    grid = np.zeros((model.grid.width, model.grid.height))

    # 遍历模型中的所有代理
    for agent in model.schedule.agents:
        if isinstance(agent, Owners):  # 确保当前代理是 Owners 类的实例
            x = int(agent.x)  # 确保 x 是整数
            y = int(agent.y)  # 确保 y 是整数

            # 打印调试信息
            print(f"Agent position: ({x}, {y}), live status: {agent.live}")

            # 检查 x 和 y 是否在有效范围内
            if 0 <= x < model.grid.width and 0 <= y < model.grid.height:
                grid[x, y] = 1 if agent.live else 0  # 根据代理的 live 状态设置网格值

    # 将 numpy 数组转换为 DataFrame
    grid_df = pd.DataFrame(grid)

    # 用 solara.DataFrame 渲染表格
    solara.DataFrame(grid_df)


def step_model():
    model.step()
    render_model()


@solara.component
def Page():
    # 创建按钮以推进模型
    solara.Button(label="Step", on_click=step_model)
    render_model()

# 如果使用 `solara run` 运行应用，Solara 会自动寻找并运行 `Page` 组件。
