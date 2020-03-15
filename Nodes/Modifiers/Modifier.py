from typing import Optional, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from Node import Node


class Modifier:
    def __init__(self, modifiers: Optional[Dict[str, float]] = None, factors:  Optional[Dict[str, float]] = None,
                 duration: int = 0) -> None:
        """

        :param duration: The duration this modifier will active, measured in ticks.
        """
        self._node = None  # type: Optional["Node"]

        self._duration = duration

        self._modifiers = {}  # type: Dict[str, float]
        if modifiers is not None:
            self._modifiers = modifiers

        self._factors = {}  # type: Dict[str, float]
        if factors is not None:
            self._factors = factors

        self._name = "Modifier"

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False

        if self.duration != other.duration:
            return False

        if self._modifiers != other._modifiers:
            return False
        if self._factors != other._factors:
            return False
        return True

    def serialize(self) -> Dict[str, Any]:
        data = {}  # type: Dict[str, Any]
        data["type"] = type(self).__name__
        data["modifiers"] = self._modifiers
        data["factors"] = self._factors
        data["duration"] = self._duration
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        self._modifiers = data["modifiers"]
        self._factors = data["factors"]
        self._duration = data["duration"]

    @property
    def duration(self):
        return self._duration

    @property
    def name(self):
        return self._name

    def setNode(self, node: "Node") -> None:
        self._node = node

    def getNode(self) -> Optional["Node"]:
        return self._node

    def getModifierForProperty(self, property: str) -> float:
        return self._modifiers.get(property, 0.)

    def getFactorForProperty(self, property: str):
        return self._factors.get(property, 1)

    def update(self) -> None:
        self._duration -= 1
        if self._duration <= 0 and self._node is not None:
            self._node.removeModifier(self)
            self._onModifierRemoved()

    def _onModifierRemoved(self) -> None:
        pass
