class Vertex:
    def __init__(self, node):
        self.idx = node
        self.visited = False

    def add_neighbor(self, neighbor, graph):
        graph.add_edge(self.idx, neighbor)

    def get_connections(self, graph):
        return graph.adj_matrix

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
        self.adj_matrix = [[-1] * self.num_vertices for _ in range(self.num_vertices)]
        self.vertices = []
        for i in range(0, num_vertices):
            new_vertex = Vertex(i)
            self.vertices.append(new_vertex)

    def set_vertex(self, vertex, idx):
        if 0 <= vertex <= self.num_vertices:
            self.vertices[vertex].set_vertex_id(idx)

    def get_vertex(self, n):
        for vertex in range(0, self.num_vertices):
            if n == self.vertices[vertex].get_vertex_id():
                return vertex
        else:
            return -1

    def add_edge(self, frm, to, cost=0):
        if self.get_vertex(frm) != -1 and self.get_vertex(to) != -1:
            self.adj_matrix[self.get_vertex(frm)][self.get_vertex(to)] = cost

    def get_vertices(self):
        vertices = []
        for vertex in range(0, self.num_vertices):
            vertices.append(self.vertices[vertex].get_vertex_id())
        return vertices

    def print_matrix(self):
        for u in range(0, self.num_vertices):
            row = []
            for v in range(0, self.num_vertices):
                row.append(self.adj_matrix[u][v])
            print(row)

    def get_edges(self):
        edges = []
        for v in range(0, self.num_vertices):
            for u in range(0, self.num_vertices):
                if self.adj_matrix[u][v] != -1:
                    vid = self.vertices[u].get_vertex_id()
                    wid = self.vertices[v].get_vertex_id()
                    edges.append((vid, wid, self.adj_matrix[u][v]))
        return edges

if __name__ == '__main__':
    G = Graph(5)
    print (G.adj_matrix)
    G.print_matrix()
    G.set_vertex(0, 'a')
    G.set_vertex(4, 'b')
    G.add_edge('a', 'b', 10)
    G.print_matrix()
    print(G.get_edges())