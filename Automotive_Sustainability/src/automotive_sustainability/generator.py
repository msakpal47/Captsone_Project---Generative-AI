import random
from typing import List, Dict


class IdeaGenerator:
    def __init__(self) -> None:
        self.themes = [
            "EV Battery Circularity",
            "Fleet Efficiency",
            "Eco-Driving Coach",
            "Supply Chain Emissions",
            "Lightweight Materials LCA",
            "Charging Strategy Optimization",
            "Predictive Maintenance for EVs",
            "Renewable Energy Integration",
        ]
        self.overviews = [
            "Develop a data-driven approach to reduce lifecycle emissions using generative scenario planning and synthetic datasets.",
            "Generate optimization strategies that balance cost, emissions, and performance across fleet operations.",
            "Create coaching insights that personalize driver behavior to minimize fuel or energy consumption.",
            "Map and estimate upstream emissions using sparse data and generative augmentation.",
            "Model material trade-offs and end-of-life pathways to improve circularity.",
            "Design charging schedules that adapt to grid signals and operational constraints.",
            "Forecast component health and propose maintenance actions to reduce downtime.",
            "Align renewable generation with demand patterns using synthetic demand profiles.",
        ]
        self.deliverables = [
            "Data schema and synthetic data generator",
            "Baseline model and optimization pipeline",
            "Evaluation dashboard with scenario exploration",
            "API for idea generation and project briefs",
            "Visualization of emissions and performance metrics",
            "Automated report templates for stakeholders",
        ]
        self.data_sources = [
            "Telematics and CAN bus signals",
            "Charging session logs and tariff data",
            "Supplier declarations and public datasets",
            "Routes, traffic, and weather feeds",
            "Maintenance records and sensor events",
            "Manufacturing BOM and material databases",
        ]
        self.metrics = [
            "CO2e reduction versus baseline",
            "Cost per km improvement",
            "Energy consumption per trip",
            "Utilization and uptime rate",
            "Route efficiency score",
            "State-of-health prediction accuracy",
        ]

    def generate_project_brief(self, topic: str, n: int = 3) -> List[Dict[str, object]]:
        items: List[Dict[str, object]] = []
        for _ in range(max(1, n)):
            title = f"{topic}: {random.choice(self.themes)}"
            overview = random.choice(self.overviews)
            ds = random.sample(self.data_sources, k=min(3, len(self.data_sources)))
            dvs = random.sample(self.deliverables, k=3)
            m = random.sample(self.metrics, k=3)
            items.append(
                {
                    "title": title,
                    "overview": overview,
                    "data_sources": ds,
                    "deliverables": dvs,
                    "evaluation_metrics": m,
                }
            )
        return items


def generate(topic: str, n: int = 3) -> List[Dict[str, object]]:
    return IdeaGenerator().generate_project_brief(topic, n)
