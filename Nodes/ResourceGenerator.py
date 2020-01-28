from Nodes.Node import Node


class ResourceGenerator(Node):
    """
    A Resource generator is, as the name implies, a node that generates a given resource every tick.
    """
    def __init__(self, node_id: str, resource_type: str, amount: float, **kwargs) -> None:
        """
        Create a Resource generator that generates a given resource every tick.
        :param node_id: Unique identifier of the node
        :param resource_type: What type of resource should it produce?
        :param amount: How much of the resource should it produce every tick?
        :param kwargs:
        """
        super().__init__(node_id, **kwargs)
        self._resource_type = resource_type.lower()
        self._amount = amount
        self._original_amount = amount

    def update(self) -> None:
        super().update()
        resources_left = self._provideResourceToOutogingConnections(self._resource_type, self._amount)

        self._resources_produced_this_tick[self._resource_type] = max(self._amount - resources_left, 0)

