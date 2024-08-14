import mesa
import random
import math
from itertools import product
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
        self.TSE = self.initial_TSE_decision() #初始阶段决定加入哪个TSE

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
    def unify_calculation(self):
        return

    # 初始选择TSE
    def initial_TSE_decision(self):
        TSE_number = 0
        return TSE_number

    # 生态转换决策
    def TSE_decision(self):
        TSE_number = 0
        return TSE_number

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
        self.demand_iteration = 0.1 #需求迭代概率
        self.live = True  # 是否还活着
        self.TSE = 0  # 初始阶段决定加入哪个TSE

        self.utility = 0  # 成本加成率
        self.market = random.randint(30, 100)
        self.production_cost = random.uniform(10, 20)  # 生产成本


    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


    def generate_ts_demand(self,know):
        return


    def generate_tech_matrix_for_category(self):

        return



    def get_average_knowledge_by_category(self):
        return

    def evaluate_satisfaction(self, platform_modules):#判断平台提供的满不满意

         return



    def Matching_evaluate_satisfaction(self, platform_modules):  # 判断平台提供的满不满意,用于匹配阶段
       return

    def Pre_evaluate(self, standard):
        return


    def upgrade(self):#需求被满足有概率提出自己的技术标准需求
        return

    def step(self):
        return

class Platform(mesa.Agent):
    """"平台"""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def generate_categories(self,n):  # 随机生成每个产业有哪几个技术模块

        return

    def collect_owners_info(self, model):#收集拥有者数据
      return


    def collect_consumers_info(self, model):#收集消费者需求

        return

    def categorize_consumers(self,model):#计算每个消费者的成本加成率
        return

    def obtain_information(self, consumers_info, owners_info):
        return

    #以收益为导向的匹配机制
    #@jit
    def match(self, consumers_info, owners_info):  # 技术标准匹配过程
        return

    def collect_average_L(self):

        return

    def step(self):
        self.owners_info = self.collect_owners_info(self.model)
        self.consumers_info = self.collect_consumers_info(self.model)
        self.obtain_information(self.consumers_info, self.owners_info)

        self.categorize_consumers(self.model)

        self.match_consumers_with_owners2(self.consumers_info, self.owners_info)
        self.avg_tech_levels, self.avg_consumer_levels = self.collect_average_L()
