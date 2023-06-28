class Vertex:
    def __init__(self, node):
        self.idx = node
        self.visited = False

    def add_neighbor(self, neighbor, graph):
        graph.add_edge(self.idx, neighbor)

    def get_connections(self, graph):
        return [graph.get_vertex_instance(i) for i, vertex in
                enumerate(graph.adj_matrix[self.get_vertex_id()])
                if vertex != -1]

    def get_vertex_id(self):
        return self.idx

    def set_vertex_id(self, idx):
        self.idx = idx

    def set_visited(self):
        self.visited = True

    def __str__(self):
        return str(self.idx)


class Graph:
    def __init__(self, num_vertices=0):
        self.num_vertices = num_vertices
        self.adj_matrix = [[-1] * self.num_vertices for _ in
                           range(self.num_vertices)]
        self.vertices = [Vertex(i) for i in range(0, self.num_vertices)]

    def set_vertex(self, vertex, idx):
        if 0 <= vertex < self.num_vertices:
            self.vertices[vertex].set_vertex_id(idx)

    def get_vertex(self, idx):
        for vertex in range(0, self.num_vertices):
            if idx == self.vertices[vertex].get_vertex_id():
                return vertex
        else:
            return -1

    def get_vertex_instance(self, idx):
        for vertex in self.vertices:
            if idx == vertex.get_vertex_id():
                return vertex

    def add_edge(self, frm, to, cost):
        if self.get_vertex(frm) != -1 and self.get_vertex(to) != -1:
            self.adj_matrix[self.get_vertex(frm)][self.get_vertex(to)] = cost
            self.adj_matrix[self.get_vertex(to)][self.get_vertex(frm)] = cost

    def delete_edge(self, frm, to):
        self.adj_matrix[frm][to] = -1
        self.adj_matrix[to][frm] = -1

    def get_vertices(self):
        return [vertex.get_vertex_id() for vertex in self.vertices]

    def print_matrix(self):
        for u in range(0, self.num_vertices):
            row = []
            for v in range(0, self.num_vertices):
                row.append(self.adj_matrix[u][v])
            print(row)

    def get_edges(self):
        edges = []
        for u in range(0, self.num_vertices):
            for v in range(0, self.num_vertices):
                if self.adj_matrix[u][v] != -1:
                    frm = self.vertices[u].get_vertex_id()
                    to = self.vertices[v].get_vertex_id()
                    edges.append((frm, to, self.adj_matrix[u][v]))
        return edges
