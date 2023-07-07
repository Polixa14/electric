import math
from apis.shorts_calculation.graph import Graph, Vertex

# Todo: refactoring, implement autotransformers


class ShortsScheme(Graph):
    def __init__(self, num_vertices=0):
        self.short_point = None
        super().__init__(num_vertices)

    def calculate_short_circuit(self, elements_list, short_point):
        self.short_point = short_point
        scheme = self.make_substitution_scheme(elements_list)
        self.configure_scheme(scheme)
        calculation_scheme = self.build_calculation_scheme()
        self.transform_to_calc_scheme()
        short_current = self.calculate_periodic_current()
        return calculation_scheme, short_current

    def calculate_periodic_current(self):
        scheme = self.build_calculation_scheme()
        short_current = 0
        for elem in scheme:
            emf = elem['params'].get('emf')
            x = elem['params'].get('reactive_resistance')
            r = elem['params'].get('active_resistance')
            z = math.sqrt(math.pow(x, 2) + math.pow(r, 2))
            short_current += (emf / z)
        return short_current

    @staticmethod
    def make_substitution_scheme(elements_list):
        """
        function to transform elements_list into scheme elements list.
        All the params we will need are resistances, location points, type and
        emf of each element
        """
        substitution_elements = []
        for element in elements_list:
            emf = None
            supertrancient_emf = None
            try:
                emf = element['element'].emf
            except AttributeError:
                pass
            try:
                supertrancient_emf = element['element'].supertrancient_emf
            except AttributeError:
                pass

            if supertrancient_emf:
                emf = (supertrancient_emf * element[
                    'element'].nominal_voltage /
                       math.sqrt(3))

            new_element = {
                "startpoint": element['startpoint'],
                "endpoint": element['endpoint'],
                "active_resistance": element['element'].active_resistance,
                "reactive_resistance": element[
                    'element'].reactive_resistance,
                "emf": emf,
                "element_type": element['element'].__class__.__name__
            }
            if element['element'].__class__.__name__ == 'Transformer':
                new_element['high_voltage'] = \
                    element['element'].nominal_voltage_high
                new_element['low_voltage'] = \
                    element['element'].nominal_voltage_low
            substitution_elements.append(new_element)
        return substitution_elements

    def build_calculation_scheme(self):
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
        return calculation_scheme

    def recreate_scheme(self, scheme):
        vertices = set()
        for element in scheme:
            vertices.add(element.get('startpoint'))
            vertices.add(element.get('endpoint'))
        self.num_vertices = len(vertices)
        self.adj_matrix = [[-1] * self.num_vertices for _ in
                           range(self.num_vertices)]
        self.vertices = [Vertex(i) for i in range(self.num_vertices)]
        self.configure_scheme(scheme, reduced=True)

    def configure_scheme(self, scheme: list[dict], reduced: bool = False):
        """
        Method fill all existing edges
        :param scheme:substitution scheme
        :param reduced: False when run first time, then always True
        """
        self.fill_scheme(scheme)
        if not reduced:
            self.reduce_to_base_voltage()
        self.look_for_triangles()

    def fill_scheme(self, scheme: list[dict]):
        """

        :param scheme: substitution scheme
        :return:
        """
        for scheme_element in scheme:
            start_vertex = scheme_element.pop('startpoint')
            end_vertex = scheme_element.pop('endpoint')
            self.set_vertex(start_vertex, start_vertex)
            self.set_vertex(end_vertex, end_vertex)
            if self.adj_matrix[start_vertex][end_vertex] != -1:
                self.merge_parallel_edges(
                    start_vertex,
                    end_vertex,
                    scheme_element
                )
            else:
                self.add_edge(start_vertex, end_vertex, scheme_element)

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

        # Two cases exist: both edges with emf or both without
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
            'reactive_resistance': result_reactive_resistance,
            'element_type': existing_edge.get('element_type')
        }

    def transform_to_calc_scheme(self):
        visited = {}
        self.transform_to_calc_scheme_recursion(
            self.get_vertex_instance(self.short_point),
            visited
        )

    def transform_to_calc_scheme_recursion(self,
                                           current_vertex,
                                           visited):
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

                # Case when vertex(common point between 2 edges)
                # has 2 connections include current vertex means edge
                # between current_vertex and vertex is series to edge
                # between vertex and its another connection
                if len(vertex_connections_exclude_current) == 1 \
                        and common_vertex_id != self.short_point:
                    last_vertex_id = \
                        vertex_connections_exclude_current[0].get_vertex_id()
                    self.sum_up_two_edges(
                        first_vertex_id,
                        common_vertex_id,
                        last_vertex_id,
                    )

                    # When two series edges added - need to check scheme for
                    # parallel edges with emf and same element type and merge
                    # them
                    self.merge_parallel_edges_with_emf()

                    # The original schema has changed - start transforming from
                    # the beginning and break current transforming
                    self.transform_to_calc_scheme()
                    break

                # When vertex connected only with current_vertex and short
                # point not on this vertex - delete it.
                elif len(vertex_connections_exclude_current) == 0 \
                        and len(vertex_connections) != 0:
                    if vertex_id != self.short_point:
                        edge = self.adj_matrix[current_vertex_id][vertex_id]
                        if not edge.get('emf'):
                            self.delete_edge(current_vertex_id, vertex_id)

                            # The original schema has changed - start
                            # transforming from the beginning and break
                            # current transforming
                            self.transform_to_calc_scheme()
                            break
                else:

                    # If nothing to sum_up/merge - go deeper
                    self.transform_to_calc_scheme_recursion(
                        vertex,
                        visited,
                    )

    def sum_up_two_edges(self,
                         first_vertex_id,
                         common_vertex_id,
                         last_vertex_id):
        """
        Method to find summary resistance of two series elements.
        If edge between two vertices already exists - merge result to existing
        edge
        """
        edge_1 = self.adj_matrix[first_vertex_id][common_vertex_id]
        edge_2 = self.adj_matrix[common_vertex_id][last_vertex_id]
        emf_1 = edge_1.get('emf')
        emf_2 = edge_2.get('emf')
        active_resistance_1 = edge_1.get('active_resistance')
        active_resistance_2 = edge_2.get('active_resistance')
        reactive_resistance_1 = edge_1.get('reactive_resistance')
        reactive_resistance_2 = edge_2.get('reactive_resistance')
        result_emf = None
        if emf_1:
            result_emf = emf_1
            e_type = edge_1.get('element_type')
        elif emf_2:
            result_emf = emf_2
            e_type = edge_2.get('element_type')
        else:
            e_type = 'result resistance'
        result_active_resistance = active_resistance_1 + active_resistance_2
        result_reactive_resistance = \
            reactive_resistance_1 + reactive_resistance_2
        new_edge = {
            "emf": result_emf,
            "active_resistance": result_active_resistance,
            "reactive_resistance": result_reactive_resistance,
            "element_type": e_type
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
                current_edge = self.adj_matrix[start_vertex][end_vertex]

                # Checking if this is an existing edge and this is an "emf"
                # edge
                if current_edge != -1 and current_edge.get('emf'):
                    parallel_edge = self.find_parallel_edge(
                        start_vertex,
                        end_vertex
                    )
                    if parallel_edge:
                        is_same_startpoint, parallel_edge_free_point = \
                            parallel_edge
                        # When parallel edge found and common point determined
                        # checking both edges have same element type
                        if is_same_startpoint:
                            self.merge_parallel_edges(
                                parallel_edge_free_point,
                                start_vertex,
                                self.adj_matrix[start_vertex][end_vertex]
                                )
                            self.delete_edge(start_vertex, end_vertex)
                        else:
                            self.merge_parallel_edges(
                                parallel_edge_free_point,
                                end_vertex,
                                self.adj_matrix[start_vertex][end_vertex]
                            )
                            self.delete_edge(start_vertex, end_vertex)

    def look_for_triangles(self):
        visited = {}
        current_vertex = self.get_vertex_instance(self.short_point)
        self.look_for_triangles_recursion(
            current_vertex,
            visited
        )

    def look_for_triangles_recursion(self,
                                     current_vertex,
                                     visited):
        current_vertex_id = current_vertex.get_vertex_id()
        visited[current_vertex_id] = True
        for vertex in current_vertex.get_connections(self):
            if vertex.get_vertex_id() not in visited:
                for next_vertex in vertex.get_connections(self):
                    if current_vertex in next_vertex.get_connections(self):
                        vertex_id = vertex.get_vertex_id()
                        next_vertex_id = next_vertex.get_vertex_id()
                        self.triangle_to_star(current_vertex_id,
                                              vertex_id,
                                              next_vertex_id)
                        break
                self.look_for_triangles_recursion(vertex,
                                                  visited)

    def triangle_to_star(self,
                         first_vertex,
                         second_vertex,
                         last_vertex):
        edge_1 = self.adj_matrix[first_vertex][second_vertex]
        edge_2 = self.adj_matrix[second_vertex][last_vertex]
        edge_3 = self.adj_matrix[last_vertex][first_vertex]
        active_resistance_1 = edge_1.get('active_resistance')
        reactive_resistance_1 = edge_1.get('reactive_resistance')
        active_resistance_2 = edge_2.get('active_resistance')
        reactive_resistance_2 = edge_2.get('reactive_resistance')
        active_resistance_3 = edge_3.get('active_resistance')
        reactive_resistance_3 = edge_3.get('reactive_resistance')
        ray_active_resistance_1 = (active_resistance_1 * active_resistance_3 /
                                   (active_resistance_1 + active_resistance_2 +
                                    active_resistance_3))
        ray_reactive_resistance_1 = (reactive_resistance_1 *
                                     reactive_resistance_3 /
                                     (reactive_resistance_1 +
                                      reactive_resistance_2 +
                                      reactive_resistance_3))

        ray_active_resistance_2 = (active_resistance_1 * active_resistance_2 /
                                   (active_resistance_1 + active_resistance_2 +
                                    active_resistance_3))
        ray_reactive_resistance_2 = (reactive_resistance_1 *
                                     reactive_resistance_2 /
                                     (reactive_resistance_1 +
                                      reactive_resistance_2 +
                                      reactive_resistance_3))

        ray_active_resistance_3 = (active_resistance_2 * active_resistance_3 /
                                   (active_resistance_1 + active_resistance_2 +
                                    active_resistance_3))
        ray_reactive_resistance_3 = (reactive_resistance_2 *
                                     reactive_resistance_3 /
                                     (reactive_resistance_1 +
                                      reactive_resistance_2 +
                                      reactive_resistance_3))
        scheme = []
        triangle_first_vertex = min(first_vertex, last_vertex, second_vertex)
        new_vertex_id = triangle_first_vertex + 1
        self.delete_edge(first_vertex, second_vertex)
        self.delete_edge(first_vertex, last_vertex)
        self.delete_edge(second_vertex, last_vertex)
        if first_vertex > triangle_first_vertex:
            first_vertex += 1
        if second_vertex > triangle_first_vertex:
            second_vertex += 1
        if last_vertex > triangle_first_vertex:
            last_vertex += 1
        scheme.extend([
            {
                "startpoint": first_vertex,
                "endpoint": new_vertex_id,
                "active_resistance": ray_active_resistance_1,
                "reactive_resistance": ray_reactive_resistance_1,
                "emf": None,
                "element_type": "result resistance"
            },
            {
                "startpoint": new_vertex_id,
                "endpoint": second_vertex,
                "active_resistance": ray_active_resistance_2,
                "reactive_resistance": ray_reactive_resistance_2,
                "emf": None,
                "element_type": "result resistance"
            },
            {
                "startpoint": new_vertex_id,
                "endpoint": last_vertex,
                "active_resistance": ray_active_resistance_3,
                "reactive_resistance": ray_reactive_resistance_3,
                "emf": None,
                "element_type": "result resistance"
            }
        ])
        for start_vertex in range(self.num_vertices):
            for end_vertex in range(self.num_vertices):
                edge = self.adj_matrix[start_vertex][end_vertex]
                self.adj_matrix[end_vertex][start_vertex] = -1
                if edge != -1:
                    new_start_vertex = start_vertex
                    new_end_vertex = end_vertex
                    if new_start_vertex > triangle_first_vertex:
                        new_start_vertex += 1
                    if new_end_vertex > triangle_first_vertex:
                        new_end_vertex += 1

                    scheme.append(
                        {
                            "startpoint": new_start_vertex,
                            "endpoint": new_end_vertex,
                            "active_resistance": edge.get('active_resistance'),
                            "reactive_resistance":
                                edge.get('reactive_resistance'),
                            "emf": edge.get('emf'),
                            "element_type": edge.get('element_type')
                        }
                    )
        if self.short_point > triangle_first_vertex:
            self.short_point += 1
        self.recreate_scheme(scheme)

    def reduce_to_base_voltage(self):
        """
        Method to reduce all params of elements to base voltage.
        Base voltage - voltage of "emf" element between 0 and 1 vertex
        """
        visited = {}
        current_vertex = self.vertices[0]
        start_edge = self.adj_matrix[0][1]
        current_voltage_rate = int(start_edge.get('emf') * math.sqrt(3))
        self.reduce_to_base_voltage_recursion(
            current_vertex,
            visited,
            current_voltage_rate
        )

    def reduce_to_base_voltage_recursion(self,
                                         current_vertex,
                                         visited,
                                         current_voltage_rate,
                                         coefficient=1):
        current_vertex_id = current_vertex.get_vertex_id()
        visited[current_vertex_id] = True
        for vertex in current_vertex.get_connections(self):
            if vertex.get_vertex_id() not in visited:
                vertex_id = vertex.get_vertex_id()

                # According to methodology - coefficient applying to all
                # resistances and emfs. On the base stage - coefficient is 1,
                # on all another - depends on transformers between base and
                # another one stage
                element = self.adj_matrix[current_vertex_id][vertex_id]
                new_active_resistance = (element.get('active_resistance') *
                                         math.pow(coefficient, 2))
                new_reactive_resistance = (element.get('reactive_resistance') *
                                           math.pow(coefficient, 2))
                emf = element.get('emf')
                new_emf = emf * coefficient if emf else emf
                new_element = {
                    "active_resistance": new_active_resistance,
                    "reactive_resistance": new_reactive_resistance,
                    "emf": new_emf,
                    "element_type": element.get('element_type')
                }
                self.add_edge(current_vertex_id, vertex_id, new_element)

                # When transformer met between two vertices - coefficient
                # must be changed according to transformer params
                if element.get('element_type') == 'Transformer':
                    transformer_high_voltage = element.get('high_voltage')
                    transformer_low_voltage = element.get('low_voltage')
                    if current_voltage_rate == transformer_high_voltage:
                        new_coefficient = (coefficient *
                                           transformer_high_voltage /
                                           transformer_low_voltage)
                        another_voltage_rate = int(transformer_low_voltage)
                    else:
                        new_coefficient = (coefficient *
                                           transformer_low_voltage /
                                           transformer_high_voltage)
                        another_voltage_rate = int(transformer_high_voltage)
                    # Going deeper to the next voltage stage after transformer
                    # with new coefficient and voltage rate
                    self.reduce_to_base_voltage_recursion(
                        vertex,
                        visited,
                        another_voltage_rate,
                        new_coefficient
                    )
                else:

                    # Going deeper in base stage
                    self.reduce_to_base_voltage_recursion(
                        vertex,
                        visited,
                        current_voltage_rate,
                        coefficient
                    )
