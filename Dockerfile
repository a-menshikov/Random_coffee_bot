FROM python:3.10

COPY requirements.txt .

WORKDIR /bot

COPY . .

RUN g++ -O3 /bot/match_algoritm/lowlewel/Example.cpp /bot/match_algoritm/lowlewel/BinaryHeap.cpp /bot/match_algoritm/lowlewel/Matching.cpp /bot/match_algoritm/lowlewel/Graph.cpp -o matchingalogitm

RUN mv /bot/matchingalogitm /bot/match_algoritm/matchingalogitm

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
