import httpx
import random

SERVICE_A_URL = "http://localhost:8001"
SERVICE_B_URL = "http://localhost:8002"

def create_game(service_url):
    response = httpx.post(f"{service_url}/game")
    response.raise_for_status()


    return response.json()


def create_match():
    game_a = create_game(SERVICE_A_URL)
    game_b = create_game(SERVICE_B_URL)

    return game_a, game_b


def make_shot(service_url, session_id):
    response = httpx.post(
        f"{service_url}/game/{session_id}/shot"
    )
    response.raise_for_status()

    return response.json()


def send_opponent_shot(service_url, session_id, coordinate):
    response = httpx.post(
        f"{service_url}/game/{session_id}/opponent-shot",
        json={"coordinate": coordinate},
    )
    response.raise_for_status()

    return response.json()


def send_shot_result(service_url, session_id, result):
    response = httpx.post(
        f"{service_url}/game/{session_id}/shot/result",
        json={"result": result},
    )
    response.raise_for_status()

    return response.json()


def close_game(service_url, session_id):
    response = httpx.post(
        f"{service_url}/game/{session_id}/close"
    )
    response.raise_for_status()

    return response.json()


def play_turn(
    shooter_url,
    shooter_session_id,
    defender_url,
    defender_session_id,
):
    shot = make_shot(
        shooter_url,
        shooter_session_id,
    )

    result = send_opponent_shot(
        defender_url,
        defender_session_id,
        shot["coordinate"],
    )

    send_shot_result(
        shooter_url,
        shooter_session_id,
        result["result"],
    )

    return shot["coordinate"], result["result"]


def is_fleet_sunk(game, hits):
    ship_coordinates = {
        coordinate
        for ship in game["ships"]
        for coordinate in ship["coordinates"]
    }
    
    return ship_coordinates.issubset(hits)


def update_hits(hits, coordinate, result):
    if result in ("hit", "killed"):
        hits.add(coordinate)

    return hits


def play_match(service_a_url, service_b_url):
    game_a, game_b = create_match()

    hits_a = set()
    hits_b = set()

    current_shooter = random.choice(["A", "B"])

    while True:
        if current_shooter == "A":
            coordinate, result = play_turn(
                service_a_url,
                game_a["session_id"],
                service_b_url,
                game_b["session_id"],
            )

            print("A:", coordinate, result)
            
            hits_b = update_hits(hits_b, coordinate, result)

            if is_fleet_sunk(game_b, hits_b):
                winner = "A"
                break

        else:
            coordinate, result = play_turn(
                service_b_url,
                game_b["session_id"],
                service_a_url,
                game_a["session_id"],
            )

            print("B:", coordinate, result)
            hits_a = update_hits(hits_a, coordinate, result)

            if is_fleet_sunk(game_a, hits_a):
                winner = "B"
                break

        current_shooter = get_next_shooter(
            current_shooter,
            result,
        )
    
    close_game(
        service_a_url,
        game_a["session_id"],
    )   
    close_game(
        service_b_url,
        game_b["session_id"],
    )

    return winner


def run_tournament(services):
    scores = {service: 0 for service in services}

    for i in range(len(services)):
        for j in range(i + 1, len(services)):
            service_a = services[i]
            service_b = services[j]

            winner = play_match(service_a, service_b)

            if winner == "A":
                scores[service_a] += 1
            else:
                scores[service_b] += 1

            print(
                f"Match: {service_a} vs {service_b}, winner: {winner}"
            )
    winner = max(scores, key=scores.get)
    return scores, winner


def get_next_shooter(current_shooter, result):
    if result == "miss":
        if current_shooter == "A":
            return "B"
        return "A"

    return current_shooter