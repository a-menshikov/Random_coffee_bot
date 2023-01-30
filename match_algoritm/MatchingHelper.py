import subprocess
import json
from loader import bot, logger, db_controller
from sendler.match_messages import send_match_messages


class MachingHelper():
    """Class - interfase for matchingalogitm1.exe"""
    vertex_conunt: int
    edges_count: int

    def __init__(self) -> None:
        logger.info("Create a MachingHelper")
        self.prepare()

    def prepare(self):
        """Prepare for machting algo"""
        logger.info("Prepare matching algo")
        data_from_bd = {}
        active_users = db_controller.select_query(
            "SELECT id FROM user_status WHERE status=1").fetchall()
        active_users = [i[0] for i in active_users]
        for now_user in active_users:
            connected_user = db_controller.select_query(
                f"SELECT met_info FROM user_mets WHERE id={now_user}").fetchone()[0]
            connected_user = list(json.loads(connected_user).values())
            data_from_bd[now_user] = connected_user

        adjacency_list = {}
        self.all_active = list(data_from_bd.keys())
        for v in self.all_active:
            adjacency_list[v] = [
                item for item in self.all_active if item not in data_from_bd[v]+[v]]
        edges = []
        for v in self.all_active:
            for i in adjacency_list[v]:
                edges.append((max(v, i), min(v, i)))
                edges = list(set(edges))
        str_edges = ""
        temp = ""
        for i in edges:
            str_edges += f"{i[0]} {i[1]} 0\n"
            temp += f"{i[0]} -- {i[1]}\n"
        self.edges_count = len(edges)
        self.vertex_conunt = max(self.all_active) + 1
        res = f"{self.vertex_conunt}\n{self.edges_count}\n{str_edges}"
        with open("./data/match_algoritm_data/input.txt", "w") as text:
            text.write(res)
        with open("./data/match_algoritm_data/temp.txt", "w") as text:
            text.write(temp)

    async def send_and_write(self, t: dict):
        """Send a mets to users"""
        logger.info("Write mets to db")
        db_controller.update_mets(t)
        db_controller.update_all_user_mets(t)
        logger.info("Start send matches")
        await send_match_messages(t, bot)

    def start(self):
        """Run matching algo"""
        logger.info("Start matching algo")
        subprocess.call(['./match_algoritm/matchingalogitm -f ./data/match_algoritm_data/input.txt --max'], shell=True)
        res = []
        print(res)
        with open("./data/match_algoritm_data/output.txt", "r") as text:
            res = text.readlines()
        res = [tuple(map(int, i[:-1].split())) for i in res]
        matches = {}
        for first, second in res:
            matches[first] = second
            self.all_active.remove(first)
            self.all_active.remove(second)
        for i in self.all_active:
            matches[i] = None
        self.matchings = matches
        logger.info("End matching algo")
        return matches
