import math
from apis.shorts_calculation.graph import Graph

# Todo: refactoring


def make_substitution_scheme(elements_list):
    """
    function to transform elements_list into scheme elements list.
    All the params we will need are resistances, location points and emf of
    each element
    """
    substitution_elements = []
    for element in elements_list:
        emf = None
        try:
            emf = element['element'].supertrancient_emf
        except AttributeError:
            pass
        substitution_elements.append(
            {
                "startpoint": element['startpoint'],
                "endpoint": element['endpoint'],
                "active_resistance": element['element'].active_resistance,
                "reactive_resistance": element['element'].reactive_resistance,
                "emf": emf
            }
        )
    return substitution_elements


def calculate_short_current(scheme):
    short_current = 0
    for elem in scheme:
        emf = elem['params'].get('emf')
        x = elem['params'].get('reactive_resistance')
        r = elem['params'].get('active_resistance')
        z = math.sqrt(math.pow(x, 2) + math.pow(r, 2))
        short_current += (emf / z)
    return short_current


class ShortsScheme(Graph):

    def calculate_short_circuit(self, elements_list, short_point):
        scheme = make_substitution_scheme(elements_list)
        self.fill_graph(scheme)
        self.transform_to_calc_scheme(short_point)
        calculation_scheme = []
        for start_vertex in range(self.num_vertices):
            for end_vertex in range(self.num_vertices):
                edge = self.adj_matrix[start_vertex][end_vertex]
                element_with_reversed_edge = {"startpoint": end_vertex,
                                              "endpoint": start_vertex,
                                              "params": edge}
                if edge != -1 and \
                        element_with_reversed_edge not in calculation_scheme:
                    calculation_scheme.append({
                        "startpoint": start_vertex,
                        "endpoint": end_vertex,
                        "params": edge
                    })
        short_current = calculate_short_current(calculation_scheme)
        return calculation_scheme, short_current

    def fill_graph(self, scheme):
        for scheme_element in scheme:
            start_vertex = scheme_element['startpoint']
            end_vertex = scheme_element['endpoint']
            params = {
                "emf": scheme_element['emf'],
                "active_resistance": scheme_element['active_resistance'],
                "reactive_resistance": scheme_element['reactive_resistance'],
            }
            self.set_vertex(start_vertex, start_vertex)
            self.set_vertex(end_vertex, end_vertex)
            """Bellow we add new edge, if edge between two vertices doesn't 
            exist, otherwise - merge two parallel edges into one.
            Another case with edges, contains EMF. For this edges we have to
            merge edges with same end/start points. Note: one of two points
            for this edges always 'free'."""
            if not params.get('emf'):
                if self.adj_matrix[start_vertex][end_vertex] != -1:
                    self.merge_parallel_edges(start_vertex, end_vertex, params)
                else:
                    self.add_edge(start_vertex, end_vertex, params)
            else:
                if not self.find_parallel_edge(start_vertex, end_vertex):
                    self.add_edge(start_vertex, end_vertex, params)
                else:
                    is_same_startpoint, parallel_edge_free_point = \
                        self.find_parallel_edge(start_vertex, end_vertex)
                    if is_same_startpoint:
                        self.merge_parallel_edges(
                            parallel_edge_free_point,
                            start_vertex,
                            params
                        )
                    else:
                        self.merge_parallel_edges(
                            parallel_edge_free_point,
                            end_vertex,
                            params
                        )

    def merge_parallel_edges(self, first_vertex, second_vertex, new_edge):
        existing_edge = self.adj_matrix[first_vertex][second_vertex]
        emf_1 = existing_edge.get('emf')
        emf_2 = new_edge.get('emf')
        active_resistance_1 = existing_edge.get('active_resistance')
        active_resistance_2 = new_edge.get('active_resistance')
        reactive_resistance_1 = existing_edge.get('reactive_resistance')
        reactive_resistance_2 = new_edge.get('reactive_resistance')
        full_resistance_1 = math.sqrt(math.pow(active_resistance_1, 2) +
                                      math.pow(reactive_resistance_1, 2))
        full_resistance_2 = math.sqrt(math.pow(active_resistance_2, 2) +
                                      math.pow(reactive_resistance_2, 2))
        result_emf = None
        if emf_1 and emf_2:
            result_emf = ((emf_1 * full_resistance_2 +
                           emf_2 * full_resistance_1) /
                          (full_resistance_1 + full_resistance_2))
        result_active_resistance = (active_resistance_1 * active_resistance_2 /
                                    (active_resistance_1 +
                                     active_resistance_2))
        result_reactive_resistance = (reactive_resistance_1 *
                                      reactive_resistance_2 /
                                      (reactive_resistance_1 +
                                       reactive_resistance_2))
        self.adj_matrix[first_vertex][second_vertex] = \
            self.adj_matrix[second_vertex][first_vertex] = {
            'emf': result_emf,
            'active_resistance': result_active_resistance,
            'reactive_resistance': result_reactive_resistance
        }

    def transform_to_calc_scheme(self, short_point):
        visited = {}
        self.transform_to_calc_scheme_recursion(
            self.get_vertex_instance(short_point),
            visited,
            short_point
        )

    def transform_to_calc_scheme_recursion(self,
                                           current_vertex,
                                           visited,
                                           short_point):
        """
        DSF traversal of graph. If next vertex has connections only with
        current vertex and another one - its means
        this vertex and current vertex are series and must be summed.
        Elif edge between curren vertex and next vertex has only resistance
        and next vertex doesn't have another connection - we should delete
        them, because it is just dead end.
        After summing graph must be checked for parallel edges with emf.
        After that method start from the short_point again.
        """
        current_vertex_id = current_vertex.get_vertex_id()
        visited[current_vertex_id] = True
        for vertex in current_vertex.get_connections(self):
            vertex_id = vertex.get_vertex_id()
            vertex_connections = vertex.get_connections(self)
            vertex_connections_exclude_current = [vertex for vertex in
                                                  vertex_connections
                                                  if vertex != current_vertex]
            if vertex.get_vertex_id() not in visited:
                first_vertex_id = current_vertex.get_vertex_id()
                common_vertex_id = vertex.get_vertex_id()
                if len(vertex_connections_exclude_current) == 1 \
                        and common_vertex_id != short_point:
                    last_vertex_id = \
                        vertex_connections_exclude_current[0].get_vertex_id()
                    self.add_two_edges(
                        first_vertex_id,
                        common_vertex_id,
                        last_vertex_id,
                    )
                    self.merge_parallel_edges_with_emf()
                    self.transform_to_calc_scheme(short_point)
                    break
                elif len(vertex_connections_exclude_current) == 0 \
                        and len(vertex_connections) != 0:
                    if vertex_id != short_point:
                        edge = self.adj_matrix[current_vertex_id][vertex_id]
                        if not edge.get('emf'):
                            self.delete_edge(current_vertex_id, vertex_id)
                            self.transform_to_calc_scheme(short_point)
                            break
                else:
                    self.transform_to_calc_scheme_recursion(
                        vertex,
                        visited,
                        short_point
                    )

    def add_two_edges(self, first_vertex_id, common_vertex_id, last_vertex_id):
        """
        Method to find summary resistance of two series elements.
        If edge between two vertices already exists - merge result to existing
        edge
        """
        emf_1 = self.adj_matrix[first_vertex_id][common_vertex_id].get('emf')
        emf_2 = self.adj_matrix[common_vertex_id][last_vertex_id].get('emf')
        active_resistance_1 = \
            (self.adj_matrix[first_vertex_id][common_vertex_id]
             .get('active_resistance'))
        active_resistance_2 = \
            (self.adj_matrix[common_vertex_id][last_vertex_id]
             .get('active_resistance'))
        reactive_resistance_1 = \
            (self.adj_matrix[first_vertex_id][common_vertex_id]
             .get('reactive_resistance'))
        reactive_resistance_2 = \
            (self.adj_matrix[common_vertex_id][last_vertex_id]
             .get('reactive_resistance'))
        result_emf = emf_1 or emf_2 or None
        result_active_resistance = active_resistance_1 + active_resistance_2
        result_reactive_resistance = \
            reactive_resistance_1 + reactive_resistance_2
        new_edge = {
            "emf": result_emf,
            "active_resistance": result_active_resistance,
            "reactive_resistance": result_reactive_resistance
        }

        if self.adj_matrix[first_vertex_id][last_vertex_id] == -1:
            self.add_edge(first_vertex_id, last_vertex_id, new_edge)
        else:
            self.merge_parallel_edges(
                first_vertex_id,
                last_vertex_id,
                new_edge
            )

        self.delete_edge(first_vertex_id, common_vertex_id)
        self.delete_edge(common_vertex_id, last_vertex_id)

    def find_parallel_edge(self, start_vertex, end_vertex):
        """
        Method looking for edge with emf adn with same start/end point.
        """
        emf_edges_with_same_endpoint = \
            [(parallel_edge_startpoint, row[end_vertex])
             for parallel_edge_startpoint, row in enumerate(self.adj_matrix)
             if row[end_vertex] != -1 and row[end_vertex].get('emf')
             and parallel_edge_startpoint != start_vertex]
        emf_edges_with_same_startpoint = \
            [(parallel_edge_endpoint, row[start_vertex])
             for parallel_edge_endpoint, row in enumerate(self.adj_matrix)
             if row[start_vertex] != -1 and row[start_vertex].get('emf')
             and parallel_edge_endpoint != end_vertex]
        if emf_edges_with_same_startpoint:
            parallel_edge_free_point, is_same_startpoint = \
                emf_edges_with_same_startpoint[0][0], True
            return is_same_startpoint, parallel_edge_free_point
        elif emf_edges_with_same_endpoint:
            parallel_edge_free_point, is_same_startpoint = \
                emf_edges_with_same_endpoint[0][0], False
            return is_same_startpoint, parallel_edge_free_point

    def merge_parallel_edges_with_emf(self):
        """
        Method travers all edges and merge edges with emf into another with
        same start/endpoint if it exists and has emf too.
        """
        for start_vertex in range(self.num_vertices):
            for end_vertex in range(self.num_vertices):
                if self.adj_matrix[start_vertex][end_vertex] != -1 and \
                        self.adj_matrix[start_vertex][end_vertex].get('emf'):
                    if self.find_parallel_edge(start_vertex, end_vertex):
                        is_same_startpoint, parallel_edge_free_point = \
                            self.find_parallel_edge(start_vertex, end_vertex)
                        if is_same_startpoint:
                            self.merge_parallel_edges(
                                parallel_edge_free_point,
                                start_vertex,
                                self.adj_matrix[start_vertex][end_vertex]
                            )
                        else:
                            self.merge_parallel_edges(
                                parallel_edge_free_point,
                                end_vertex,
                                self.adj_matrix[start_vertex][end_vertex]
                            )
                        self.delete_edge(start_vertex, end_vertex)

    def delete_edges_without_emf(self, short_point):
        for start_vertex in range(self.num_vertices):
            for end_vertex in range(self.num_vertices):
                edge = self.adj_matrix[start_vertex][end_vertex]
                if edge != -1 and not edge.get('emf'):
                    start_connections_count = len(self.get_vertex_instance(
                        start_vertex
                    ).get_connections(self))
                    end_connections_count = len(self.get_vertex_instance(
                        end_vertex
                    ).get_connections(self))
                    if (start_connections_count == 1 and
                        start_vertex != short_point) or \
                            (end_connections_count == 1 and
                             end_vertex != short_point):
                        self.delete_edge(start_vertex, end_vertex)
