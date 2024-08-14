import mesa
from Agents import Owners,Consumers,Platform
from model import TSAE

RICH_COLOR = "#2ca02c"
# Red
POOR_COLOR = "#d62728"
# Blue
MID_COLOR = "#1f77b4"
def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Owners:
        portrayal["Shape"] = "resource/owners.png"
        # https://icons8.com/web-app/433/sheep
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1


    if type(agent) is Consumers:
        portrayal["Shape"] = "resource/consumers.png"
        # https://icons8.com/web-app/433/sheep
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2


    if type(agent) is Platform:
        portrayal["Shape"] = "resource/platform.png"
        # https://icons8.com/web-app/433/sheep
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    return portrayal

grid = mesa.visualization.CanvasGrid(wolf_sheep_portrayal, 30, 30, 500, 500)
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Num_Owners", "Color": "Blue"},
        {"Label": "Num_Consumers", "Color": "Red"}
    ]
)
chart_element1 = mesa.visualization.ChartModule(
    [
        {"Label": "Match_Success_Rate", "Color": "Green"},
        {"Label": "satisfaction_rate", "Color": "Red"},
    ]
)
chart_element2 = mesa.visualization.ChartModule(
    [
        {"Label": "Avg_Wealth_Owners", "Color": "Blue"},

    ]
)
chart_element3 = mesa.visualization.ChartModule(
    [

        {"Label": "Avg_Wealth_Consumers", "Color": "Red"}
    ]
)
agent_bar1 = mesa.visualization.BarChartModule(
    [{"Label": "Wealth", "Color": "Blue"}],scope="agent",


)

pie_chart = mesa.visualization.PieChartModule(
    [
        {"Label": "Num_Owners", "Color": "Green"},
        {"Label": "Num_Consumers", "Color": "Red"},
    ]
)
model_params = {
    "N": mesa.visualization.Slider(
        "Number of agents",
        40,
        2,
        40,
        1,
        description="Choose how many agents to include in the model",
    ),
    "width": 30,
    "height": 30,
}

server = mesa.visualization.ModularServer(
    TSAE, [grid,chart_element,chart_element1,chart_element2,chart_element3,agent_bar1,], "TASE", model_params
)
server.port = 7777
