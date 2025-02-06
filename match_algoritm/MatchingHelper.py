import json
import subprocess

from controllerBD.db_loader import Session
from controllerBD.models import UserMets, UserStatus
from controllerBD.services import (
    send_message_to_admins,
    update_all_user_mets,
    update_mets,
)
from handlers.user.check_message import check_message
from loader import bot, logger
from sendler.match_messages import send_match_messages


class MachingHelper:
    """Класс - интерфейс алгоритма"""

    vertex_conunt: int
    edges_count: int

    def __init__(self) -> None:
        logger.info("Create a MachingHelper")
        self.prepare()

    def prepare(self):
        """Подготовка алгоритма"""
        logger.info("Начало подготовки работы алгоритма")
        with Session() as db_session:
            data_from_bd = {}
            active_users = (
                db_session.query(UserStatus.id).filter(UserStatus.status == 1).all()
            )
            active_users = [i[0] for i in active_users]
            for now_user in active_users:
                connected_user = (
                    db_session.query(UserMets.met_info)
                    .filter(UserMets.id == now_user)
                    .first()
                )
                if connected_user:
                    connected_user = connected_user[0]
                else:
                    new_record = UserMets(id=now_user, met_info="{}")
                    db_session.add(new_record)
                    db_session.commit()
                    connected_user = "{}"
                connected_user = list(set(json.loads(connected_user).values()))
                data_from_bd[now_user] = connected_user

        logger.debug(f"data_from_bd: {data_from_bd}")
        adjacency_list = {}
        self.all_active = list(data_from_bd.keys())
        for v in self.all_active:
            candidates = [
                item for item in self.all_active if item not in data_from_bd[v] + [v]
            ]
            if not candidates:
                candidates = [item for item in self.all_active if item != v]
            adjacency_list[v] = candidates
        logger.debug(f"adjacency_list: {adjacency_list}")
        edges = []
        for v in self.all_active:
            for i in adjacency_list[v]:
                edges.append((max(v, i), min(v, i)))
                edges = list(set(edges))
                logger.debug(edges)
        str_edges = ""
        temp = ""
        for i in edges:
            str_edges += f"{i[0]} {i[1]} 0\n"
            temp += f"{i[0]} -- {i[1]}\n"
        self.edges_count = len(edges)
        self.vertex_conunt = max(self.all_active) + 1
        res = f"{self.vertex_conunt}\n{self.edges_count}\n{str_edges}"
        logger.debug(f"res: {res}")
        with open("./data/match_algoritm_data/input.txt", "w") as text:
            text.write(res)
        with open("./data/match_algoritm_data/temp.txt", "w") as text:
            text.write(temp)
        logger.info("Завершение подготовки работы алгоритма")

    async def send_and_write(self, t: dict):
        """Запись результатов в базу и рассылка сообщений"""
        logger.info("Начало записи новых встреч в базу")
        await update_mets(t)
        update_all_user_mets(t)
        logger.info("Завершение записи новых встреч в базу")
        logger.info("Начало рассылки сообщений о новых встречах")
        await send_match_messages(t, bot)

    def start(self):
        """Запуск алгоритма"""
        logger.info("Начало работы алгоритма")
        subprocess.call(
            [
                "./match_algoritm/matchingalogitm -f ./data/match_algoritm_data/input.txt --max"
            ],
            shell=True,
        )
        res = []
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
        logger.info("Завершение работы алгоритма")
        logger.info(f"пары {matches}")
        return matches


async def start_algoritm():
    """Запуск алгоритма распределения"""
    await send_message_to_admins("Начинаем распределение")
    await check_message()
    mc = MachingHelper()
    res = mc.start()
    await send_message_to_admins(
        f"Количество пар: {len(res)}.\n" f"Начинаем отправку сообщений."
    )
    await mc.send_and_write(res)
    await send_message_to_admins(
        "Сообщения пользователям отправлены.\n" "Распределение завершено."
    )
