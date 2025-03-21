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
        self.live = True #是否还活着
        self.TSE = self.initial_TSE()  # 初始阶段决定加入哪个TSE

        self.module = self.initial_module()
        self.level = self.generation_Level()  # 技术等级
        self.PrimeLevel = self.level #初始等级
        self.revenue = {}  # 每个周期的收益字典
        self.network_coeff = 0.1  # 网络效应系数
        self.enter_cost = 20  # 生态进入成本
        self.inertia_coeff = 0.1  # 惯性成本系数
        self.enter_time = 0  # 进入生态的时间
        self.x = random.uniform(0, 1)  # 战略空间坐标x
        self.y = random.uniform(0, 1)  # 战略空间坐标y
        self.strategy_coeff = 50.0  # 战略选择成本系数
        self.test = 0 # 技术测试费用
        self.Period_cost = 0 #周期性消耗

        #策略4 承诺策略
        self.order = 1 if random.uniform(0, 1) > 0.2 else 0

    # 确保周期初始每个模块都有技术
    def initial_module(self):
        if self.model.schedule.steps == 0:
            Onwer_in_category = [agent for agent in self.model.schedule.agents
                                 if isinstance(agent, Owners) and agent.TSE == self.TSE]

            required_modules = set(range(1, 7))
            existing_modules = {agent.module for agent in Onwer_in_category}
            missing_modules = required_modules - existing_modules
            if missing_modules:
                chosen_module = missing_modules.pop()
            else:
                chosen_module = random.randint(1, 6)
        else:
            chosen_module = random.randint(1, 6)

        return chosen_module

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
            Level = random.randint(max_level - 2, max_level + 2) #均匀分布
        else:
            Level = random.randint(1, 6) #初始阶段的技术等级为[1.6]
        return Level

    # 初始化时随机进入两个生态
    def initial_TSE(self):
        period = self.model.schedule.steps
        number = 0
        if period == 0:
            number = random.randint(1,2)

        return number

    # 效用计算
    def unify_calculation(self, TSE_number, TSE_x, TSE_y, current_TSE):
        period = self.model.schedule.steps
        Onwer_in_category = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Owners) and agent.TSE == TSE_number]

        if self.TSE == 0:
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
                overall_average_revenue = 0
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

        # 读取平台
        platform_same = [agent for agent in self.model.schedule.agents if
                                        isinstance(agent, Platform) and agent.TSE == TSE_number]

        Fee = 0
        if platform_same[0].butie_module[self.module-1] == 1:
            Fee = platform_same[0].butie_Fee

        utility = (overall_average_revenue
                    # 策略3 资源独占，还没写完
                   + Fee
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
        if ((total_Onwer_in_SameTSE - min_diff) - (total_Onwer_in_SameTSE - max_diff)) != 0:
            x = (diff_list[self.module - 1] - min_diff) / (max_diff - min_diff)
        else:
            x = 0

        diff_list2 = [len(Onwer_in_SameTSE_each[module]) for module in range(1, 7)]
        max_diff2 = max(diff_list2)
        min_diff2 = min(diff_list2)
        # 计算 y 值
        if (max_diff2 - min_diff2) != 0:
            y = (diff_list2[self.module - 1] - min_diff2) / (max_diff2 - min_diff2)
        else:
            y = 0

        return x, y

    # 选择TSE
    def TSE_decision(self):
        x1, y1 = self.x_y_calculation(1)
        x2, y2 = self.x_y_calculation(2)
        utility1 = self.unify_calculation(1, x1, y1, self.TSE)
        utility2 = self.unify_calculation(2, x2, x2, self.TSE)
        time = self.model.schedule.steps
        Platform1 = [agent for agent in self.model.schedule.agents if
                            isinstance(agent, Platform) and agent.TSE == 1]


        Platform2 = [agent for agent in self.model.schedule.agents if
                            isinstance(agent, Platform) and agent.TSE == 2]

        if utility1 > utility2:
            if self.TSE == 1:
                self.enter_time += 1
                self.wealth += Platform1[0].butie_Fee
            else:
                self.TSE = 1
                self.enter_time = 1
                self.test = Platform1[0].test
                self.Period_cost = Platform1[0].Period_cost_provider
                self.wealth += Platform1[0].butie_Fee
        else:
            if self.TSE == 2:
                self.enter_time += 1
                self.wealth += Platform2[0].butie_Fee
            else:
                self.TSE = 2
                self.enter_time = 1
                self.test = Platform2[0].test
                self.Period_cost = Platform2[0].Period_cost_provider
                self.wealth += Platform2[0].butie_Fee


    # 技术升级决策
    def upgrade(self):
        flag = False # 判断是否创新成功
        Fee_max = 50  # 升级费用阈值
        Fee = min(random.uniform(0, 0.42 * self.wealth), Fee_max)  # 升级技术费用
        Possible = min(Fee / Fee_max, 0.9)   # 升级成功概率

        #选取在同一个TSE中，模块相同的owner
        Onwer_in_catogery = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Owners) and agent.module == self.module and agent.TSE == self.TSE]
        average_Level = sum(agent.level for agent in Onwer_in_catogery) / len(Onwer_in_catogery)

        #技术升级决策
        if self.level < average_Level:
            if random.uniform(0, 1) <= Possible:
                self.level = self.level + 1
                flag = True
            self.wealth = self.wealth - Fee

        return flag


    def step(self):
        self.move()
        if self.model.schedule.steps > 1:
            self.TSE_decision()
        Sucess_weather = self.upgrade()
        if Sucess_weather:
            self.wealth -= self.test
        return

class Consumers(mesa.Agent):
    """技术标准消费者"""

    def __init__(self, unique_id, model):

        super().__init__(unique_id, model)
        self.wealth = random.uniform(100, 120)  # 初始资本量
        #self.match_threshold = random.randint(5, 15) # 阈值
        self.match_threshold = 10
        self.demand_iteration = 0.8 # 需求迭代概率
        self.Match_time = 0 # 等待匹配的周期
        self.satisfaction = False # 是否满意技术标准
        self.live = True  # 是否还活着
        self.period_cost = 0 #周期性消耗
        self.develop_cost = 1 #单位jishushengjichengben
        self.market = random.randint(30, 100)
        self.production_cost = random.uniform(10, 20)  # 生产成本

        # 获取技术模块，并生成初始技术水平
        platform_instance = next(agent for agent in model.schedule.agents if isinstance(agent, Platform))
        self.categories = platform_instance.categories
        self.knowledge = self.generate_tech_matrix(self.categories)

        self.demand = self.generate_ts_demand(self.knowledge) # 标准需求
        self.TSE = self.initial_TSE()  # 初始阶段决定加入哪个TSE

        #效用函数计算相关参数
        self.x = random.uniform(0, 1)  # 战略空间坐标x
        self.y = random.uniform(0, 1)  # 战略空间坐标y

        self.revenue = {}  # 每个周期的收益字典
        self.network_coeff = 0.05  # 网络效应系数
        self.enter_cost = 5  # 生态进入成本
        self.inertia_coeff = 0.05  # 惯性成本系数
        self.enter_time = 0  # 进入生态的时间
        self.strategy_coeff = 50.0  # 战略选择成本系数

        #市场相关参数
        self.cost_coeff = random.uniform(0, 1)  # 成本加成率
        self.Price = (1 + self.cost_coeff) * self.production_cost # 市场价格
        self.fie1 = 0.5 # 价格系数
        self.fie2 = 5 # 性能系数

        # 策略4 承诺策略
        self.order = 1 if random.uniform(0, 1) > 0.2 else 0

        self.Platform = []

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def initial_TSE(self):
        period = self.model.schedule.steps
        number = 0
        if period == 0:
            number = random.randint(1, 2)

        return number
    #效用函数计算
    def unify_calculation(self, TSE_number, TSE_x, TSE_y, current_TSE):
        period = self.model.schedule.steps
        Consumers_in_category = [agent for agent in self.model.schedule.agents if
                                 isinstance(agent, Consumers) and agent.TSE == TSE_number]

        if self.TSE == 0:
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

            # 计算所有Consumer的平均revenue
            if average_revenue_values:  # 确保列表不为空
                overall_average_revenue = sum(average_revenue_values) / len(average_revenue_values)
            else:
                overall_average_revenue = 0
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
                   + len(Consumers_in_category) * self.network_coeff
                   - self.enter_cost
                   - self.inertia_coeff * self.enter_time
                   - self.strategy_coeff * math.sqrt((self.x - TSE_x) ** 2 + (self.y - TSE_y) ** 2))

        a = self.strategy_coeff * math.sqrt((self.x - TSE_x) ** 2 + (self.y - TSE_y) ** 2)

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
                max_levels.append(0)  # 如果当前模块没有agent，保存None
                min_levels.append(0)  # 如果当前模块没有agent，保存None

        numerator = 0
        denominator = 0
        for module in range(1, 7):
            numerator += self.knowledge[module - 1]
            denominator += max_levels[module - 1]

        # 计算 x 值
        if denominator != 0:
            x = numerator/denominator
        else:
            x = 0

        numerator = 0
        denominator = 0
        for module in range(1, 7):
            numerator += abs(self.knowledge[module - 1] - first_platform.technology_standard[module - 1])
            g1 = abs(first_platform.technology_standard[module - 1] - max_levels[module - 1])
            g2 = abs(first_platform.technology_standard[module - 1] - min_levels[module - 1])
            denominator += max(g1, g2)

        # 计算 y 值
        if denominator != 0:
            y = 1 - numerator/denominator
        else:
            y = 1

        return x, y

    def TSE_decision(self):
        x1, y1 = self.x_y_calculation(1)
        x2, y2 = self.x_y_calculation(2)
        utility1 = self.unify_calculation(1, x1, y1, self.TSE)
        utility2 = self.unify_calculation(2, x2, y2, self.TSE)
        Platform1 = [agent for agent in self.model.schedule.agents if
                         isinstance(agent, Platform) and agent.TSE == 1]
        Platform2 = [agent for agent in self.model.schedule.agents if
                     isinstance(agent, Platform) and agent.TSE == 2]

        if utility1 > utility2:
            if self.TSE == 1:
                self.enter_time += 1
                self.Platform = Platform1[0]
            else:
                self.TSE = 1
                self.enter_time = 1
                self.period_cost = Platform1[0].Period_cost_consumer
                self.satisfaction = False
                self.Platform = Platform1[0]
        else:
            if self.TSE == 2:
                self.enter_time += 1
                self.Platform = Platform2[0]
            else:
                self.TSE = 2
                self.enter_time = 1
                self.period_cost = Platform2[0].Period_cost_consumer
                self.satisfaction = False
                self.Platform = Platform2[0]

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
                tech_level = random.randint(0, 5)
                tech_vertex.append(tech_level)

            # 根据生态情况生成技术水平
            else:
                min_tech = int(min_tech_level[module - 1])
                max_tech = max(int(max_tech_level[module - 1]), 2)

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
            return [0, 0, 0, 0, 0, 0]

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
            return [0, 0, 0, 0, 0, 0]

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
        technology_standards = [platform.technology_standard for platform in Platform_involved][0]

        total_difference = 0 # 总差距
        TS_ultify = False   # 有效性


        #判断技术标准是否有效
        for consumer_level, consumer_demand, module_level in zip(self.knowledge, self.demand, technology_standards):
            if 0 == module_level:
                break
            if consumer_level < module_level:
                TS_ultify = True
                total_difference = total_difference + module_level - consumer_level

        # 若有效则进行满意
        if TS_ultify == True and total_difference <= self.match_threshold:
            # 技术采用
            for i in range(len(technology_standards)):
                if technology_standards[i] > self.knowledge[i]:
                    self.knowledge[i] = technology_standards[i]

            self.satisfaction = True
            self.Match_time = 0
            self.wealth -= total_difference * self.develop_cost
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

    # 市场份额和产品性能计算,返回市场份额和总收益
    def market_calculation(self):
        Platform_Same = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Platform) and agent.TSE == self.TSE]
        TS = [platform.technology_standard for platform in Platform_Same][0]

        Platform_Other = [agent for agent in self.model.schedule.agents if
                         isinstance(agent, Platform) and agent.TSE != self.TSE]
        TS_other = [platform.technology_standard for platform in Platform_Other][0]

        total_tech_level_same = sum(TS)
        total_tech_level_other = sum(TS_other)

        # 计算技术标准的比值
        num = 1
        if self.TSE == 1:
            num = 1
        else:
            if total_tech_level_same != 0:
                num = total_tech_level_other/total_tech_level_same
            else:
                num = 1

        # 计算市场需求
        market_reality = self.market - self.fie1 * self.Price + self.fie2 * num
        total_revenue = market_reality * self.Price
        return market_reality, total_revenue

    def step(self):
        self.move()
        if self.model.schedule.steps > 0:
            self.TSE_decision()
        if self.satisfaction == True:
            self.Demand_iterate()


class Platform(mesa.Agent):
    """"平台"""

    def __init__(self, unique_id, model, number, discount, butie_module,
                 butie_Fee):
        super().__init__(unique_id, model)
        self.TSE = number
        self.CF = random.uniform(20, 40)  # 产品认证费用
        self.wealth = random.uniform(1000, 1500)  # 平台初始资本量
        self.live = True # 是否还活着
        self.categories = [1, 2, 3, 4, 5, 6] # 领域
        self.technology_standard = [0, 0, 0, 0, 0, 0]  # 技术标准
        self.Provider_participate = [] # 参与当前标准制定的providers
        self.Period_cost_consumer = random.randint(5, 10) # 向需求者收取的周期性费用
        self.Period_cost_provider = random.randint(10, 20) # 向拥有者收取的周期性费用
        self.test = random.randint(20, 30)

        # 策略1 低价策略
        self.discount = discount

        # 策略3 资源独占策略
        self.butie_module = butie_module
        self.butie_Fee = butie_Fee

    # 计算每个消费者的成本加成率
    def categorize_consumers(self,model):
        return

    # 策略 1  低价策略
    def strategy_low_price(self):
        self.Period_cost_consumer *= self.discount
        self.Period_cost_provider *= self.discount


    #以匹配数量为导向进行技术标准的匹配
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
            # 对每个模块中的每个 owner 对象，获取其 level 属性并存储在新的子列表中
            levels = [owner.level for owner in owners]

            # 将该模块的 level 列表添加到 OnwerLevel 中
            OnwerLevel.append(levels)

        # 遍历每个子列表，并去除重复项
        OnwerLevel = [list(set(module_levels)) for module_levels in OnwerLevel]

        # 读取Demanders
        Demander_in_catogery = [agent for agent in self.model.schedule.agents if
                             isinstance(agent, Consumers) and agent.TSE == self.TSE]

        Best_TS = self.technology_standard # Best_TS记录最好的技术标准
        Max_Match_nunber = 0  #记录匹配数量
        for combination in itertools.product(*OnwerLevel):
            Match_number = 0
            for demander in Demander_in_catogery:
                if demander.Pre_evaluate(list(combination)):
                    # 策略4
                    if demander.order == 1:
                        Match_number += 2
                    else:
                        Match_number += 1
            if Match_number > Max_Match_nunber:
                Max_Match_nunber = Match_number
                Best_TS = list(combination)

        if Best_TS is not None and Max_Match_nunber > 0:
            self.technology_standard = Best_TS

        # 记录技术标准的来源
        Participate_provider = [[] for _ in range(6)]
        Provider_TS = []
        for module in range(1, 7):
            Participate_provider[module - 1] = [agent for agent in self.model.schedule.agents
                                                if isinstance(agent, Owners)
                                                and agent.TSE == self.TSE
                                                and agent.module == module
                                                and agent.level == self.technology_standard[module - 1]]

            # 承诺策略
            if Participate_provider[module - 1]:
                # 筛选 order == 1
                prioritized_agents = [agent for agent in Participate_provider[module - 1] if agent.order == 1]

                # 判断是否存在承诺的个体
                if prioritized_agents:
                    selected_agent = random.choice(prioritized_agents)
                else:
                    selected_agent = random.choice(Participate_provider[module - 1])
                Provider_TS.append(selected_agent)
            else:
                Provider_TS.append(None)  # 如果列表为空，添加 None 表示没有可选 agent
        self.Provider_participate = Provider_TS

        return Best_TS, Provider_TS



