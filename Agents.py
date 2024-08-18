import mesa
import random
import itertools

import math
from random import randint
from numba import jit
class Owners(mesa.Agent):
    """技术拥有者"""

    def __init__(self, unique_id, model):

        super().__init__(unique_id, model)
        self.wealth = random.uniform(100, 120)  # 初始资本量
        self.module = random.randint(1, 6)  # 随机一个技术模块
        self.level = self.generation_Level()  # 技术等级
        self.PrimeLevel = self.level #初始等级
        self.live = True #是否还活着
        self.TSE = 0  # 初始阶段决定加入哪个TSE
        self.revenue = {}  # 每个周期的收益字典
        self.network_coeff = 0.1  # 网络效应系数
        self.enter_cost = 20  # 生态进入成本
        self.inertia_coeff = 0.1  # 惯性成本系数
        self.enter_time = 0  # 进入生态的时间
        self.x = random.uniform(0, 1)  # 战略空间坐标x
        self.y = random.uniform(0, 1)  # 战略空间坐标y
        self.strategy_coeff = 0.1  # 战略选择成本系数

    # 主体移动
    def move(self):#每次移动一个格子
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        return

    # 技术等级生成
    def generation_Level(self):
        Onwer_in_category = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Owners) and agent.module == self.module]

        if Onwer_in_category and self.model.schedule.steps > 0:
            max_level = max(owner.level for owner in Onwer_in_category)
            min_level = min(owner.level for owner in Onwer_in_category)
            if min_level + 1 < max_level - 1:
                Level = random.randint(min_level + 1, max_level - 1) #均匀分布
            else:
                Level = min_level  # 排除特殊情况
        else:
            Level = random.randint(1, 6) #初始阶段的技术等级为[1.6]
        return Level

    # 效用计算
    def unify_calculation(self, TSE_number, TSE_x, TSE_y, current_TSE):
        period = self.model.schedule.steps()

        if self.TSE == 0:
            Onwer_in_category = [agent for agent in self.model.schedule.agents if
                                 isinstance(agent, Owners) and agent.TSE == TSE_number]

            # 初始化一个列表来存储每个 Owner 的过去10个step的平均revenue值
            average_revenue_values = []

            for owner in Onwer_in_category:
                # 获取过去10个step的revenue值
                revenues = []
                for i in range(max(0, period - 10), period):
                    # 如果revenue存在，则添加，否则添加0
                    revenues.append(owner.revenue.get(i, 0))

                # 计算过去10个step的平均revenue
                if revenues:
                    average_revenue = sum(revenues) / len(revenues)
                else:
                    average_revenue = 0

                average_revenue_values.append(average_revenue)

            # 计算所有Owners的平均revenue
            if average_revenue_values:  # 确保列表不为空
                overall_average_revenue = sum(average_revenue_values) / len(average_revenue_values)
        else:
            # 计算自身过去10个周期的收益平均值
            revenues = []
            for i in range(max(0, period - 10), period):
                # 获取自身revenue，如果revenue不存在，则为0
                revenues.append(self.revenue.get(i, 0))

            # 计算自身的平均收益
            if revenues:
                overall_average_revenue = sum(revenues) / len(revenues)
            else:
                overall_average_revenue = 0

        utility = (overall_average_revenue
                   + len(Onwer_in_category) * self.network_coeff
                   - self.enter_cost * abs(current_TSE - TSE_number)
                   - self.inertia_coeff * self.enter_time
                   - self.strategy_coeff * math.sqrt((self.x - TSE_x) ** 2 + (self.y - TSE_y) ** 2))
        return utility

    # 战略坐标计算
    def x_y_calculation(self, TSE_number):
        # 获取所有 TSE 为number 的 Owner agents
        Onwer_in_SameTSE = [agent for agent in self.model.schedule.agents if
                            isinstance(agent, Owners) and agent.TSE == TSE_number]

        # 计算 Onwer_in_SameTSE 的总数量
        total_Onwer_in_SameTSE = len(Onwer_in_SameTSE)

        # 初始化字典
        Onwer_in_SameTSE_each = {}

        # 将  module 匹配的 agents 按模块存储在字典中
        for module in range(1, 7):
            Onwer_in_SameTSE_each[module] = [agent for agent in Onwer_in_SameTSE if agent.module == module]

        # 计算1*6的列表，每个元素是总数量减去每个模块的数量
        diff_list = [total_Onwer_in_SameTSE - len(Onwer_in_SameTSE_each[module]) for module in range(1, 7)]

        # 计算最大值和最小值
        max_diff = max(diff_list)
        min_diff = min(diff_list)

        # 计算 x 值
        x = ((total_Onwer_in_SameTSE - len(Onwer_in_SameTSE_each[self.module])) - (
                total_Onwer_in_SameTSE - max_diff)) / (
                    (total_Onwer_in_SameTSE - min_diff) - (total_Onwer_in_SameTSE - max_diff))

        # 计算 y 值
        y = (len(Onwer_in_SameTSE_each[self.module]) - min_diff) / (max_diff - min_diff)

        return x, y

    # 选择TSE
    def TSE_decision(self):
        x1, y1 = self.x_y_calculation(1)
        x2, y2 = self.x_y_calculation(2)
        utility1 = self.unify_calculation(1, x1, x2, self.TSE)
        utility2 = self.unify_calculation(2, x1, x2, self.TSE)
        if utility1 > utility2:
            if self.TSE == 1:
                self.enter_time += 1
            else:
                self.TSE = 1
                self.enter_time = 1
        else:
            if self.TSE == 2:
                self.enter_time += 1
            else:
                self.TSE = 2
                self.enter_time = 1

    # 技术升级决策
    def upgrade(self):
        Fee_max = 200  # 升级费用阈值
        Fee = min(random.uniform(0, 0.42 * self.wealth), Fee_max)  # 升级技术费用
        Possible = min(Fee / Fee_max, 0.8)   # 升级成功概率

        #选取在同一个TSE中，模块相同的owner
        Onwer_in_catogery = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Owners) and agent.module == self.module and agent.TSE == self.TSE]
        average_Level = sum(agent.level for agent in Onwer_in_catogery) / len(Onwer_in_catogery)

        #技术升级决策
        if self.level < average_Level:
            if random.uniform(0, 1) <= Possible:
                self.level = self.level + 1
            self.wealth = self.wealth - Fee
        return


    def step(self):
        self.move()
        self.TSE_decision()
        self.upgrade()
        return

class Consumers(mesa.Agent):
    """技术标准消费者"""

    def __init__(self, unique_id, model):

        super().__init__(unique_id, model)
        self.wealth = random.uniform(100, 120)  # 初始资本量
        self.match_threshold = 6 # 阈值
        self.demand_iteration = 0.1 # 需求迭代概率
        self.Match_time = 0 # 等待匹配的周期
        self.satisfaction = False # 是否满意技术标准
        self.live = True  # 是否还活着

        self.utility = 0  # 成本加成率
        self.market = random.randint(30, 100)
        self.production_cost = random.uniform(10, 20)  # 生产成本

        # 获取技术模块，并生成初始技术水平
        platform_instance = next(agent for agent in model.schedule.agents if isinstance(agent, Platform))
        self.categories = platform_instance.categories
        self.knowledge = self.generate_tech_matrix(self.categories)

        self.demand = self.generate_ts_demand(self.knowledge) # 标准需求
        self.TSE = 0  # 初始阶段决定加入哪个TSE

        self.x = random.uniform(0, 1)  # 战略空间坐标x
        self.y = random.uniform(0, 1)  # 战略空间坐标y

        self.revenue = {}  # 每个周期的收益字典
        self.network_coeff = 0.1  # 网络效应系数
        self.enter_cost = 5  # 生态进入成本
        self.inertia_coeff = 0.1  # 惯性成本系数
        self.enter_time = 0  # 进入生态的时间


    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    #效用函数计算，还未完成
    def unify_calculation(self, TSE_number, TSE_x, TSE_y, current_TSE):
        period = self.model.schedule.steps()

        if self.TSE == 0:
            Consumers_in_category = [agent for agent in self.model.schedule.agents if
                                 isinstance(agent, Consumers) and agent.TSE == TSE_number]

            # 初始化一个列表来存储每个 Owner 的过去10个step的平均revenue值
            average_revenue_values = []

            for owner in Consumers_in_category:
                # 获取过去10个step的revenue值
                revenues = []
                for i in range(max(0, period - 10), period):
                    # 如果revenue存在，则添加，否则添加0
                    revenues.append(owner.revenue.get(i, 0))

                # 计算过去10个step的平均revenue
                if revenues:
                    average_revenue = sum(revenues) / len(revenues)
                else:
                    average_revenue = 0

                average_revenue_values.append(average_revenue)

            # 计算所有Owners的平均revenue
            if average_revenue_values:  # 确保列表不为空
                overall_average_revenue = sum(average_revenue_values) / len(average_revenue_values)
        else:
            # 计算自身过去10个周期的收益平均值
            revenues = []
            for i in range(max(0, period - 10), period):
                # 获取自身revenue，如果revenue不存在，则为0
                revenues.append(self.revenue.get(i, 0))

            # 计算自身的平均收益
            if revenues:
                overall_average_revenue = sum(revenues) / len(revenues)
            else:
                overall_average_revenue = 0

        utility = (overall_average_revenue
                   + len(Onwer_in_category) * self.network_coeff
                   - self.enter_cost
                   - self.inertia_coeff * self.enter_time
                   - self.strategy_coeff * math.sqrt((self.x - TSE_x) ** 2 + (self.y - TSE_y) ** 2))
        return utility

    def x_y_calculation(self, TSE_number):
        # 获取所有 TSE 为number 的 Owner agents
        Onwer_in_SameTSE = [agent for agent in self.model.schedule.agents if
                            isinstance(agent, Owners) and agent.TSE == TSE_number]

        Platform_in_SameTSE = [agent for agent in self.model.schedule.agents if
                            isinstance(agent, Platform) and agent.TSE == TSE_number]

        first_platform = Platform_in_SameTSE[0] if Platform_in_SameTSE else None

        # 初始化字典
        Onwer_in_SameTSE_each = {}

        # 初始化两个列表，用于存储每个模块中的最大值和最小值
        max_levels = []
        min_levels = []

        # 将  module 匹配的 agents 按模块存储在字典中
        for module in range(1, 7):
            Onwer_in_SameTSE_each[module] = [agent.level for agent in Onwer_in_SameTSE if agent.module == module]

            if Onwer_in_SameTSE_each[module]:  # 确保列表不为空
                max_levels.append(max(Onwer_in_SameTSE_each[module]))  # 保存当前模块中的最大level值
                min_levels.append(min(Onwer_in_SameTSE_each[module]))  # 保存当前模块中的最小level值
            else:
                max_levels.append(None)  # 如果当前模块没有agent，保存None
                min_levels.append(None)  # 如果当前模块没有agent，保存None

        numerator = 0
        denominator = 0
        for module in range(1,7):
            numerator += self.knowledge[module]
            denominator += max_levels[module]

        # 计算 x 值
        x = numerator/denominator

        numerator = 0
        denominator = 0
        for module in range(1, 7):
            numerator += abs(self.knowledge[module] - first_platform.technology_standard[module])
            g1 = abs(self.knowledge[module] - max_levels[module])
            g2 = abs(self.knowledge[module] - min_levels[module])
            denominator += min(g1,g2)

        # 计算 y 值
        y = 1 - numerator/denominator

        return x,y

    def TSE_decision(self):
        x1, y1 = self.x_y_calculation(1)
        x2, y2 = self.x_y_calculation(2)
        utility1 = self.unify_calculation(1, x1, x2, self.TSE)
        utility2 = self.unify_calculation(2, x1, x2, self.TSE)
        if utility1 > utility2:
            if self.TSE == 1:
                self.enter_time += 1
            else:
                self.TSE = 1
                self.enter_time = 1
        else:
            if self.TSE == 2:
                self.enter_time += 1
            else:
                self.TSE = 2
                self.enter_time = 1

    # 初始化标准需求
    def generate_ts_demand(self,know):
        # 为每个技术模块的水平值生成随机值
        tech_standard_requirement = [level + random.randint(0, 2) for level in know]
        return tech_standard_requirement
        # 需求被满足有概率提出自己的技术标准需求

    # 需求迭代
    def Demand_iterate(self):
        if random.random() < self.demand_iteration:
            tech_standard_requirement = [level + random.randint(0, 2) for level in self.knowledge]
            self.demand = tech_standard_requirement
            self.satisfaction = False

    # 生成技术水平
    def generate_tech_matrix(self, categories):
        max_tech_level = self.get_max_tech_level()
        min_tech_level = self.get_min_tech_level()
        tech_vertex = []
        for module in categories:
            # 初始化生成技术水平
            if self.model.schedule.steps == 0:
                tech_level = random.randint(0, 2)
                tech_vertex.append(tech_level)

            # 根据生态情况生成技术水平
            else:
                print(min_tech_level[module])
                min_tech = int(min_tech_level[module-1])
                max_tech = int(max_tech_level[module-1])

                # 确保最大值大于最小值，避免 random.randint 抛出异常
                if max_tech - min_tech > 2:  # 需要至少有一个合法的整数范围
                    tech_level = random.randint(min_tech + 1, max_tech - 1)
                    tech_vertex.append(tech_level)
                else:
                    # 如果范围不合法，可以选择如何处理，例如设置默认值或跳过
                    tech_vertex.append(min_tech + 1)  # 或者根据需求设置一个合理的默认值

        return tech_vertex

    # 求最高技术水平
    def get_max_tech_level(self):
        # 获取所有消费者
        consumers_in_category = [agent for agent in self.model.schedule.agents if
                                 isinstance(agent, Consumers)]

        # 如果 consumers_in_category 为空，直接返回空列表
        if not consumers_in_category:
            return []

        # 初始化max_tech_level为知识列表长度的最小值
        max_tech_level = [float('-inf')] * len(consumers_in_category[0].knowledge)

        # 对每个消费者的知识进行遍历，找出每个位置上的最大值
        for consumer in consumers_in_category:
            max_tech_level = [max(max_val, knowledge) for max_val, knowledge in zip(max_tech_level, consumer.knowledge)]

        return max_tech_level

    # 求最低技术水平
    def get_min_tech_level(self):
        # 获取所有消费者
        consumers_in_category = [agent for agent in self.model.schedule.agents if
                                 isinstance(agent, Consumers)]

        # 如果 consumers_in_category 为空，直接返回空列表
        if not consumers_in_category:
            return []

        # 初始化max_tech_level为知识列表长度的最小值
        min_tech_level = [float('inf')] * len(consumers_in_category[0].knowledge)

        # 对每个消费者的知识进行遍历，找出每个位置上的最大值
        for consumer in consumers_in_category:
            min_tech_level = [min(max_val, knowledge) for max_val, knowledge in zip(min_tech_level, consumer.knowledge)]

        return min_tech_level

    # 求平均技术水平
    def get_average_tech_level(self):
        # 获取所有消费者
        consumers_in_category = [agent for agent in self.model.schedule.agents if
                                 isinstance(agent, Consumers)]

        # 初始化技术等级和技术水平的累加变量
        total_tech_level = [0] * len(consumers_in_category[0].knowledge)

        # 对每个消费者的知识进行累加
        for consumer in consumers_in_category:
            total_tech_level = [total + knowledge for total, knowledge in zip(total_tech_level, consumer.knowledge)]

        num_consumers = len(consumers_in_category)
        average_tech_level = [total / num_consumers for total in total_tech_level]
        return average_tech_level


    # 标准的满意度评估
    def evaluate_satisfaction(self):
        Platform_involved = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Platform) and agent.TSE == self.TSE]

        total_difference = 0 # 总差距
        TS_ultify = False   # 有效性
        technology_standards = [platform.technology_standard for platform in Platform_involved]

        #判断技术标准是否有效
        for consumer_level, consumer_demand, module_level in zip(self.knowledge, self.demand, technology_standards):
            if 0 == module_level:
                break
            if consumer_level < module_level:
                TS_ultify = True
                total_difference = total_difference + module_level - consumer_level

        # 若有效则进行满意
        if TS_ultify == True and total_difference <= self.match_threshold:
            self.satisfaction = True
            self.Match_time = 0
        else:
            self.satisfaction = False
            self.Match_time += 1

    # 标准满意度预评估
    def Pre_evaluate(self, standard):
        total_difference = 0  # 总差距
        TS_ultify = False  # 有效性

        # 判断技术标准是否有效
        for consumer_level, consumer_demand, module_level in zip(self.knowledge, self.demand, standard):
            if 0 == module_level:
                break
            if consumer_level < module_level:
                TS_ultify = True
                total_difference = total_difference + module_level - consumer_level

        # 若有效则进行满意
        if TS_ultify == True and total_difference <= self.match_threshold:
            return True
        else:
            return False

    def step(self):
        self.move()
        self.TSE_decision()
        if self.satisfaction == True:
            self.Demand_iterate()


class Platform(mesa.Agent):
    """"平台"""

    def __init__(self, unique_id, model, number):
        super().__init__(unique_id, model)
        self.TSE = number
        self.TF = random.uniform(30, 50)  # 技术测试费用
        self.CF = random.uniform(20, 40)  # 产品认证费用
        self.wealth = random.uniform(1000, 1500)  # 平台初始资本量
        self.live = True # 是否还活着
        self.categories = [1, 2, 3, 4, 5, 6] # 领域

    # 计算每个消费者的成本加成率
    def categorize_consumers(self,model):
        return


    #以收益为导向的匹配机制
    #@jit
    def match(self):  # 技术标准匹配过程
        # 初始化一个包含 6 个空列表的列表，用于存储每个模块的 Owners 对象
        Onwer_in_category = [[] for _ in range(6)]

        # 遍历模块编号，并将符合条件的 Owners 对象加入到相应的列表中
        for module in range(1, 7):
            Onwer_in_category[module - 1] = [agent for agent in self.model.schedule.agents
                                                  if isinstance(agent,
                                                                Owners) and agent.TSE == self.TSE and agent.module == module]
        # 初始化一个新的列表，用于存储每个模块的 owner 的 self.level 属性
        OnwerLevel = []

        # 遍历每个模块的列表
        for owners in Onwer_in_category:
            # 对每个模块中的每个 owner 对象，获取其 self.level 属性并存储在新的子列表中
            levels = [owner.self.level for owner in owners]

            # 将该模块的 level 列表添加到 OnwerLevel 中
            OnwerLevel.append(levels)

        # 遍历每个子列表，并去除重复项
        OnwerLevel = [list(set(module_levels)) for module_levels in OnwerLevel]

        # 读取Demanders
        Demander_in_catogery = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Consumers) and agent.TSE == self.TSE]

        Best_TS = [] # 记录最好的技术标准
        Max_Match_nunber = 0  #记录匹配数量
        for combination in itertools.product(*OnwerLevel):
            Match_number = 0
            for demander in Demander_in_catogery:
                if demander.Pre_evaluate(combination):
                    Match_number += 1
            if Match_number>Max_Match_nunber:
                Max_Match_nunber = Match_number
                Best_TS = combination

        self.technology_standard = Best_TS


    def step(self):
        self.match()
