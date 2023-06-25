from apis.shorts_calculation.graph import Graph
from apparatus.models import Transformer, AutoTransformer, SyncMotor, AsyncMotor, Line


class EquivalentCircuit(Graph):
    def find_parralel_edges(self):
        all_edges = []
        for edge in self.get_edges():
            all_edges.append((edge[0], edge[1]))
        breakpoint()



def make_equivalent_circuit(data):
    vertices = get_vertices(data)
    circuit = EquivalentCircuit(len(vertices))
    for scheme_element in data:
        start_vertex = scheme_element['startpoint']
        end_vertex = scheme_element['endpoint']
        element = scheme_element['element']
        circuit.set_vertex(start_vertex, start_vertex)
        circuit.set_vertex(end_vertex, end_vertex)
        circuit.add_edge(start_vertex, end_vertex, element.full_resistance_complex)
    breakpoint()
    circuit.find_parralel_edges()


def get_vertices(data):
    vertices = set()
    for scheme_element in data:
        start_vertex = scheme_element['startpoint']
        end_vertex = scheme_element['endpoint']
        vertices.add(start_vertex)
        vertices.add(end_vertex)
    return vertices



def calculate_shorts(data):
    equivalent_circuit = make_equivalent_circuit(data)
