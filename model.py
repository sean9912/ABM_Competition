import mesa
from Agents import Owners, Consumers, Platform
import random
import time
import pandas as pd


class TSAE(mesa.Model):
    def __init__(self, width=30, height=30, match_threshold=6, demand_iteration=0.1, enter_owner_num=1,
                 enter_demander_num=3, discount1=0.5, discount2=0.5, Enter_time = 0, butie_module = [False, False, False, False, False, False],
                 butie_fee = 0):
        # 重写
        self.match_threshold = match_threshold
        self.demand_iteration = demand_iteration
        self.enter_owner_num = enter_owner_num
        self.enter_demander_num = enter_demander_num

        # 主体参数
        self.a = 0.5  # 价格系数
        self.b = 5  # 效用系数
        self.current_id = 0  # 添加current_id属性

        # 收益分配系数
        self.profit_coff1 = 0.1
        self.profit_coff2 = 0.2
        self.profit_coff3 = 0.7

        # 主体坐标
        self.width = width
        self.height = height

        # 初始数量
        self.num_agents_TO = 23
        self.num_agents_TSS = 21

        # 进入数量
        self.num_owners = enter_owner_num
        self.num_consumers = enter_demander_num

        # 系统参数
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivationByType(self)  # 随机agent
        self.schedule = mesa.time.BaseScheduler(self)  # 按顺序遍历agent

        # 统计数据
        self.successful_matches = 0  # 成功匹配的
        self.total_matches = 0  # 进行匹配的
        self.datacollector = mesa.DataCollector(
            model_reporters={}
        )

        # 创建平台1
        platform1 = Platform(self.next_id(), self, 1, discount1,
                             [0, 0, 0, 0, 0, 0], 0)
        # 加入网格
        x = int((self.width / 2) + 1)
        y = int(self.height / 2)
        self.grid.place_agent(platform1, (x, y))
        self.schedule.add(platform1)

        # 策略2 延时进入策略
        if self.schedule.steps == Enter_time:
            # 创建平台2
            platform2 = Platform(self.next_id(), self, 2, discount2, butie_module, butie_fee)
            # 加入网格
            x = int((self.width / 2))
            y = int((self.height / 2))
            self.grid.place_agent(platform2, (x, y))
            self.schedule.add(platform2)

        # 创建初始owner
        for i in range(self.num_agents_TO):
            owners = Owners(self.next_id(), self)
            # 加入网格
            x = self.random.randrange(0, int(self.width / 2))
            y = self.random.randrange(self.height)
            self.grid.place_agent(owners, (x, y))
            self.schedule.add(owners)

        # 创建初始demander
        for i in range(self.num_agents_TSS):
            consumers = Consumers(self.next_id(), self)
            # 加入网格
            x = self.random.randrange(int(self.width / 2), self.width)
            y = self.random.randrange(self.height)
            self.grid.place_agent(consumers, (x, y))
            self.schedule.add(consumers)

        # 开始运行
        self.running = True
        self.datacollector.collect(self)

    def calculate_match_success_rate(self):
        return

    # 计算满意度的比例
    def calculate_satisfaction_rate(self):
        Demander_total = [agent for agent in self.schedule.agents if
                          isinstance(agent, Consumers)]
        Demander_in_catogery1 = [agent for agent in self.schedule.agents if
                                 isinstance(agent, Consumers) and agent.TSE == 1]
        Demander_in_catogery2 = [agent for agent in self.schedule.agents if
                                 isinstance(agent, Consumers) and agent.TSE == 2]

        Satification_total = sum(agent for agent in Demander_total if agent.satisfaction == True) / sum(Demander_total)
        Satification_1 = sum(agent for agent in Demander_in_catogery1 if agent.satisfaction == True) / sum(Demander_in_catogery1)
        Satification_2 = sum(agent for agent in Demander_in_catogery2 if agent.satisfaction == True) / sum(Demander_in_catogery2)

        return Satification_total, Satification_1, Satification_2

    # 周期性移除Agent
    def remove_negative_wealth_agents(self):
        negative_wealth_agents = [agent for agent in self.schedule.agents if agent.wealth < 0]
        for agent in negative_wealth_agents:
            # 如果agent是Platform代理，则跳过当前迭代
            if isinstance(agent, Platform):
                continue
            self.schedule.remove(agent)
            self.grid.remove_agent(agent)

    # 周期性进入新的主体
    def add_random_agents(self, num_owners, num_consumers):
        for i in range(num_owners):
            owner = Owners(self.next_id(), self)
            x = self.random.randrange(0, int(self.width / 2))
            y = self.random.randrange(self.height)
            self.grid.place_agent(owner, (x, y))
            self.schedule.add(owner)

        for i in range(num_consumers):
            consumer = Consumers(self.next_id(), self)
            x = self.random.randrange(int(self.width / 2), self.width)
            y = self.random.randrange(self.height)
            self.grid.place_agent(consumer, (x, y))
            self.schedule.add(consumer)

    # 标准匹配
    def match_result(self):
        Platform1 = [agent for agent in self.schedule.agents if
                     isinstance(agent, Platform) and agent.TSE == 1]
        Platform2 = [agent for agent in self.schedule.agents if
                     isinstance(agent, Platform) and agent.TSE == 2]

        TS1 = Platform1[0].match()
        TS2 = Platform2[0].match()

    # 收益分配
    def profit_distribution(self):
        consumers = [agent for agent in self.schedule.agents if
                     isinstance(agent, Consumers)]

        for consumer in consumers:
            consumer.evaluate_satisfaction()
            if consumer.satisfaction:
                # 需求者分收益
                market_reality, total_revenue = consumer.market_calculation()
                #consumer.wealth += consumer.wealth + self.profit_coff3 * total_revenue - market_reality * consumer.production_cost - consumer.period_cost
                consumer.wealth += consumer.wealth + self.profit_coff3 * total_revenue

                # 平台分收益
                platform_same = [agent for agent in self.schedule.agents if
                             isinstance(agent, Platform) and agent.TSE == consumer.TSE]
                platform_same[0].wealth += total_revenue * self.profit_coff2

                #提供者收益
                for agent in platform_same[0].Provider_participate:
                    agent.wealth += total_revenue * self.profit_coff1

        return

    def capital_settlement(self):
        # 需求者资本结算
        consumers = [agent for agent in self.schedule.agents if
                     isinstance(agent, Consumers)]

        for consumer in consumers:
            market_reality, total_revenue = consumer.market_calculation()
            consumer.wealth = consumer.wealth - market_reality * consumer.production_cost - consumer.period_cost

        # 技术提供者资本结算
        Providers = [agent for agent in self.schedule.agents if
                     isinstance(agent, Owners)]

        for provider in Providers:
            # 投资已计算过，技术测试费用已统计
            provider.wealth = provider.wealth -provider.Period_cost


    def information_collect(self):
        Demander_total = [agent for agent in self.schedule.agents if
                          isinstance(agent, Consumers)]
        Demander_in_catogery1 = [agent for agent in self.schedule.agents if
                                 isinstance(agent, Consumers) and agent.TSE == 1]
        Demander_in_catogery2 = [agent for agent in self.schedule.agents if
                                 isinstance(agent, Consumers) and agent.TSE == 2]
        Provider_total = [agent for agent in self.schedule.agents if
                          isinstance(agent, Owners)]
        Provider_in_catogery1 = [agent for agent in self.schedule.agents if
                                 isinstance(agent, Owners) and agent.TSE == 1]
        Provider_in_catogery2 = [agent for agent in self.schedule.agents if
                                 isinstance(agent, Owners) and agent.TSE == 2]

        print(len(Demander_total), len(Demander_in_catogery1), len(Demander_in_catogery2))
        print(len(Provider_total), len(Provider_in_catogery1), len(Provider_in_catogery2))


    def step(self):
        self.schedule.step()
        self.information_collect() #
        self.match_result() # 标准制定和匹配
        self.profit_distribution() # 收益分配
        self.capital_settlement() # 资本结算
        self.remove_negative_wealth_agents()  # 出
        self.add_random_agents(self.enter_owner_num, self.enter_demander_num)  # 进
        self.datacollector.collect(self) # 数据收集

    def run_model(self, n):
        for i in range(n):
            self.step()


if __name__ == "__main__":
    # 初始化一个空 DataFrame，用于存储所有模型运行的结果
    all_results = pd.DataFrame()

    for run in range(1, 11):
        model = TSAE()
        # 记录循环开始时间
        start_time = time.time()

        for i in range(600):
            end_time = time.time()
            model.step()
            print("Step:", i, "Time:", end_time - start_time, "seconds")

        print("Total time:", end_time - start_time, "seconds")
        # 将模型运行结果添加到总体结果中
        gini = model.datacollector.get_model_vars_dataframe()
        all_results = pd.concat([all_results, gini])
        file_name = f"model_data_revenue_{run:.2f}.csv"
        gini.to_csv(file_name)
