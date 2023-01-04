import subprocess
import asyncio

class MachingHelper():
    vertex_conunt:int
    edges_count:int

    def __init__(self) -> None:
        self.prepare()

    def prepare(self):
        # беру данные из бд
        data_from_bd = {
            1:[2,3],
            2:[1,4],
            3:[1],
            4:[2],
            5:[]
        }
        adjacency_list = {}
        self.all_active = data_from_bd.keys()
        for v in self.all_active:
            adjacency_list[v] = [item for item in self.all_active if item not in data_from_bd[v]+[v]]
        edges = []
        for v in  self.all_active:
            for i in adjacency_list[v]:
                edges.append((max(v,i),min(v,i)))
                edges = list(set(edges))
        str_edges = ""
        temp = ""
        for i in edges:
            str_edges+=f"{i[0]} {i[1]} 0\n"
            temp+=f"{i[0]} -- {i[1]}\n"
        self.edges_count = len(edges)
        self.vertex_conunt = len(self.all_active) + 1
        res = f"{self.vertex_conunt}\n{self.edges_count}\n{str_edges}"
        with open("./data/match_algoritm_data/input.txt","w") as text:
            text.write(res)
        with open("./data/match_algoritm_data/temp.txt","w") as text:
            text.write(temp)



    def start(self):
        subprocess.call('./match_algoritm/matchingalogitm -f ./data/match_algoritm_data/input.txt --max')
        res = []
        with open("./data/match_algoritm_data/output.txt", "r") as text:
            res = text.readlines()
        res = [tuple(map(int,i[:-1].split())) for i in res]
        t = {}
        for i in self.all_active:
            t[i] = None
        for i in res:
            a = i[0]
            b = i[1]
            t[a] = b
            t[b] = a 
        return t

    def _start_from_here(self):
        subprocess.call('./matchingalogitm -f ./input.txt --max')
        res = []
        with open("./data/match_algoritm_data/output.txt", "r") as text:
            res = text.readlines()
        res = [tuple(map(int,i[:-3].split())) for i in res]
        return res

if __name__ == "__main__":
    help = MachingHelper()
    # asyncio.run(help._start_from_here)