from dataclasses import dataclass
from typing import List, Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from models.rich_vrp import Place, Depot
    from models.rich_vrp.agent_type import AgentType
    from models.rich_vrp.costs import AgentCosts


@dataclass
class Agent:
    """Агент, который может перемещаться и выполнять задачи."""
    id: int

    costs: AgentCosts  # на сколько дорого обходится использование средства (fixed, time, distance)
    amounts: List[int]

    time_windows: List[Tuple[int, int]]  # список временных окон
    compatible_depots: Set[Depot]  # депо, в которые можно приезжать

    start_place: Place  # стартовая точка
    end_place: Place  # конечная точка прибытия

    type: AgentType = None  # тип этого конкретного агента
    priority: int = 0  # этого курьера мы хотим использовать раньше

    name: str = ""
