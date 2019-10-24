from typing import List, TYPE_CHECKING, Dict

from Connection import Connection
from Signal import signalemitter, Signal


@signalemitter
class Node:
    preUpdateCalled = Signal()
    updateCalled = Signal()
    postUpdateCalled = Signal()

    def __init__(self, node_id: str) -> None:
        '''
        :param node_id: Unique identifier of the node.
        '''
        self._node_id = node_id
        self._incoming_connections = []  # type: List[Connection]
        self._outgoing_connections = []  # type: List[Connection]

        self._resources_required_per_tick = {}  # type: Dict[str, float]
        self._resources_received_this_tick = {}  # type: Dict[str, float]
        self._resources_produced_this_tick = {}  # type: Dict[str, float]

        self.temperature = 20
        self._weight = 300

    @property
    def weight(self):
        return self._weight

    def addHeat(self, heat_to_add):
        print("ADDING heat!", heat_to_add, self._node_id)

        self.temperature += heat_to_add / self.weight
        print("NEW TEMP", self._node_id, self.temperature)

    def subtractHeat(self, heat_to_subtract):
        print("REMOVING HEAT", heat_to_subtract)
        self.temperature -= heat_to_subtract / self.weight
        print("NEW TEMP", self._node_id, self.temperature)

    def __repr__(self):
        return "Node ('{node_id}', a {class_name})".format(node_id = self._node_id, class_name = type(self).__name__)

    def updateReservations(self) -> None:
        pass

    def getId(self):
        return self._node_id

    def getResourcesRequiredPerTick(self):
        return self._resources_required_per_tick

    def getResourcesReceivedThisTick(self):
        return self._resources_received_this_tick

    def getResourcesProducedThisTick(self):
        return self._resources_produced_this_tick

    def preUpdate(self) -> None:
        self.preUpdateCalled.emit(self)
        for resource_type in self._resources_required_per_tick:
            connections = self.getAllIncomingConnectionsByType(resource_type)
            if len(connections) == 0:
                # Can't get the resource at all!
                return
            resource_to_reserve = self._resources_required_per_tick[resource_type] / len(connections)
            for connection in connections:
                connection.reserveResource(resource_to_reserve)

    def _getReservedResourceByType(self, resource_type) -> float:
        result = 0
        for connection in self.getAllIncomingConnectionsByType(resource_type):
            result += connection.getReservedResource()
        return result

    def _getAllReservedResources(self):
        for resource_type in self._resources_required_per_tick:
            self._resources_received_this_tick[resource_type] = self._getReservedResourceByType(resource_type)

    def replanReservations(self):
        for resource_type in self._resources_required_per_tick:

            connections = self.getAllIncomingConnectionsByType(resource_type)
            total_resource_deficiency = sum([connection.getReservationDeficiency() for connection in connections])
            num_statisfied_reservations = len([connection for connection in connections if connection.isReservationStatisfied()])
            if num_statisfied_reservations == 0:
                extra_resource_to_ask_per_connection = 0
            else:

                extra_resource_to_ask_per_connection = total_resource_deficiency / num_statisfied_reservations
            for connection in connections:
                if not connection.isReservationStatisfied():
                    # So the connection that could not meet demand needs to be locked (since we can't get more!)
                    connection.lock()
                else:
                    if extra_resource_to_ask_per_connection == 0:

                        connection.lock()
                        continue
                    # So the connections that did give us that we want might have a bit more!
                    print("New amount reserved:", connection.reserved_requested_amount + extra_resource_to_ask_per_connection)
                    connection.reserveResource(connection.reserved_requested_amount + extra_resource_to_ask_per_connection)

    def update(self) -> None:
        self.updateCalled.emit(self)
        self._getAllReservedResources()

    def postUpdate(self) -> None:
        self.postUpdateCalled.emit(self)
        for connection in self._outgoing_connections:
            connection.reset()
        self._resources_received_this_tick = {}
        self._resources_produced_this_tick = {}

    def requiresReplanning(self) -> bool:
        num_statisfied_reservations = len([connection for connection in self._incoming_connections if connection.isReservationStatisfied()])
        if not num_statisfied_reservations:
            return False
        else:
            return len(self._incoming_connections) != num_statisfied_reservations

    def connectWith(self, resource_type: str, target: "Node") -> None:
        new_connection = Connection(origin=self, target=target, resource_type = resource_type)
        self._outgoing_connections.append(new_connection)
        target.addConnection(new_connection)

    def addConnection(self, connection: Connection) -> None:
        self._incoming_connections.append(connection)

    def getAllIncomingConnectionsByType(self, resource_type: str) -> List[Connection]:
        return [connection for connection in self._incoming_connections if connection.resource_type == resource_type]

    def getAllOutgoingConnectionsByType(self, resource_type: str) -> List[Connection]:
        return [connection for connection in self._outgoing_connections if connection.resource_type == resource_type]

    def preGetResource(self, resource_type: str, amount: float) -> float:
        '''
        How much resources would this node be to give if we were to actually do it.
        :param resource_type:
        :param amount:
        :return:
        '''
        return 0

    def preGiveResource(self, resource_type: str, amount: float) -> float:
        '''
        How much resources would this node be able to accept if provideResource is called
        :param resource_type:
        :param amount:
        :return:
        '''
        return 0

    def getResource(self, resource_type: str, amount: float) -> float:
        return 0  # By default, we don't have the resource. Go home.

    def giveResource(self, resource_type: str, amount: float) -> float:
        return 0