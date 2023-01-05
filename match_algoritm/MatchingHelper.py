import subprocess
from importlib.machinery import SourceFileLoader
import json
from loader import bot
from sendler.match_messages import send_match_messages

class MachingHelper():
    vertex_conunt:int
    edges_count:int

    def __init__(self, db_controller) -> None:
        self.db_controller = db_controller
        self.prepare()

    def prepare(self):
        data_from_bd = {}
        active_users = self.db_controller.select_query("SELECT id FROM user_status WHERE status=1").fetchall()
        active_users = [i[0] for i in active_users]
        for now_user in active_users:
            connected_user = self.db_controller.select_query(f"SELECT met_info FROM user_mets WHERE id={now_user}").fetchone()[0]
            connected_user = list(json.loads(connected_user).values())
            # connected_user = list(map(int,connected_user.split()))
            data_from_bd[now_user] = connected_user

        # беру данные из бд
        # data_from_bd = {
        #     1:[2,3],
        #     2:[1,4],
        #     3:[1],
        #     4:[2],
        #     5:[]
        # }
        adjacency_list = {}
        self.all_active = list(data_from_bd.keys())
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

    def send_and_write(self, t: dict):
        self.db_controller.update_all_user_mets(t)
        send_match_messages(t, bot)

    def start(self):
        subprocess.call('./match_algoritm/matchingalogitm -f ./data/match_algoritm_data/input.txt --max')
        res = []
        with open("./data/match_algoritm_data/output.txt", "r") as text:
            res = text.readlines()
        res = [tuple(map(int,i[:-1].split())) for i in res]
        t = {}
        # for i in self.all_active:
        #     t[i] = None
        # for i in res:
        #     a = i[0]
        #     b = i[1]
        #     t[a] = b
        #     t[b] = a 
        for first, second in res:
            t[first] = second
            self.all_active.remove(first)
            self.all_active.remove(second)
        for i in self.all_active:
            t[i] = None
        self.matchings = t
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