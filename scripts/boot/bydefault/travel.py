import time
from typing import Union, Any
import enum

LED_TIME = 5 * 60
EVN_TIME = 2 * 60

class Direction(enum.Enum):
    Departure = "departure"
    Arrival = "arrival"

Point = tuple[float, float]
Route = tuple[str, str, Union[str, list[Point]], bool] # (destination, fragment, filename | points), reverse
DirectedRoute = tuple[Direction, Route]
WeightedRoutes = list[tuple[float, DirectedRoute]] # [(probability, directed_route)]

class Place:
    def __init__(self, internal: list[Route], external: list[Route], intext: bool) -> Place:
        self.internal = internal
        self.external = external
        self.intext = intext

# internal 
InternalRoute = tuple[str, str, str, str] # start, end, fragment, filename
ExternalRoute = tuple[str, str, list[Point]] # start, end, route

class CityMap:
    def __init__(self, internal: list[InternalRoute], external: list[ExternalRoute], intext: list[str]) -> CityMap:
        self.internal = internal
        self.external = external
        self.intext = intext

def get_place(name: str, citymap: CityMap) -> Place:
    internal_direct = [x for x in citymap.internal if x[0] == name]
    internal_direct: list[Route] = [(x[1], x[2], x[3], False) for x in internal_direct]

    internal_reverse = [x for x in citymap.internal if (x[1] == name and x[0] != x[1])]
    internal_reverse: list[Route] = [(x[0], x[2], x[3], True) for x in internal_reverse]

    external_direct = [x for x in citymap.external if x[0] == name]
    external_direct: list[Route] = [(x[1], x[2], x[3], False) for x in external_direct]

    external_reverse = [x for x in citymap.external if (x[1] == name and x[0] != x[1])]
    external_reverse: list[Route] = [(x[0], x[2], x[3], True) for x in external_reverse]

    intext = (name in citymap.intext)

    return Place(internal_direct + internal_reverse, external_direct + external_reverse, intext)

def select_route(routes: WeightedRoutes) -> DirectedRoute:
    probs = [x[0] for x in routes]
    values = [x[1] for x in routes]

    return random.choices(values, weights=probs)[0][1]

# returns 
def make_weight(routes: list[DirectedRoute], citymap: CityMap, time_to_leave) -> WeightedRoutes:
    # TODO check if destination point is going to airport and time_to_leave, use this route
    # TODO add probability map
    return [(1, route) for route in routes]

def get_route(current: tuple[Direction, str], citymap: CityMap, time_to_leave: bool) -> DirectedRoute:
    # get point parameter by name
    point = get_place(current[1], citymap)

    directed_routes: list[DirectedRoute] = []

    if len(point.external) == 0:
        # there is no external routes, go to another internal
        directed_routes = [(Direction.Departure, route) for route in point.internal]
    else:
        # there is external or intext point
        if current[0] == Direction.Departure:
            # we come from another internal point
            if point.intext:
                # special case: point external but behaves as internal
                directed_routes = [(Direction.Departure, route) for route in point.internal]
                directed_routes += [(Direction.Arrival, route) for route in point.external]
            else:
                # go to external, to other fragment
                directed_routes = [(Direction.Arrival, route) for route in point.external]
        else:
            # we come from external point, go to internal
            directed_routes = [(Direction.Departure, route) for route in point.internal]

    directed_routes = make_weight(directed_routes, citymap, time_to_leave)
    
    return select_route(routes)

def travel_city(name: str, timeout: float, citymap: CityMap):
    current = (Direction.Departure, name)
    current_time = time.time()

    while (time.time() - current_time) < timeout || current[1] != name:
        directed_route = get_route((), citymap, time_to_leave = (time.time() - current_time) > timeout)

        route = directed_route[1]
        current = (directed_route[0], route[0])

        current_time = time.time()

        if typeof(route) == "string":
            # get points from file
            points = parse_svg(route[2])
        else:
            points = route

        # construct TravelController from fragment (route[1])
        # move by points

def travel():
    # go from home position to "pulkovo"
    travel_city("pulkovo", LED_TIME, CITYMAP["led"])
    # go from "pulkovo" to "zvartnots"
    travel_city("zvartnots", EVN_TIME, CITYMAP["evn"])