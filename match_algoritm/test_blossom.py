from datetime import datetime

import blossom


def test():
    start_time = datetime.now()
    graph = blossom.Graph()
    edges = []
    graph.add_edges(edges)
    print("added in", datetime.now() - start_time)
    print(datetime.now())
    matching = blossom.Matching()
    matching.add_vertices(graph.get_vertices())
    actual = sorted(blossom.get_maximum_matching(graph, matching, 0).edges)
    print("end in", datetime.now() - start_time)
    with open("./new.txt", "w") as text:
        text.write(str(actual))


if __name__ == "__main__":
    test()
