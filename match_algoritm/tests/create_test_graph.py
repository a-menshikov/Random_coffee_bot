import random

res = {}
res2 = []
n = 5000
q = 10000
for i in range(n):
    res[i] = []
for i in range(q):
    first = random.randint(0, n - 1)
    second = random.randint(0, n - 1)
    while first == second:
        first = random.randint(0, n - 1)
        second = random.randint(0, n - 1)
    t = (max(first, second), min(first, second))
    res2.append(t)
    res2 = list(set(res2))
with open("../input.txt", "w") as text:
    res = list(sorted(res2))
    st = ""
    st += f"{n}\n{q}\n"
    for i in res:
        st += str(i[0]) + " " + str(i[1]) + " 0\n"

    text.write(st)

# for https://programforyou.ru/graph-redactor
with open("./graph.txt", "w") as text:
    df = ""
    for i in res:
        df += str(i[0]) + " -- " + str(i[1]) + "\n"
    text.write(df)
