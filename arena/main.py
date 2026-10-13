import httpx
import random
import uuid
from placement import validate_fleet

SERVICE_A_URL = "http://localhost:8001"
SERVICE_B_URL = "http://localhost:8002"

def create_game(service_url):
    try:
        response = httpx.post(
            f"{service_url}/game",
            timeout=1.0,
        )
        response.raise_for_status()

    except httpx.TimeoutException:
        raise ValueError("Service timeout")

    except httpx.HTTPError:
        raise ValueError("Service error")

    try:
        game = response.json()

    except ValueError:
        raise ValueError("Invalid service response")

    if not isinstance(game, dict):
        raise ValueError("Invalid service response")

    if "session_id" not in game or "ships" not in game:
        raise ValueError("Invalid service response")

    if not isinstance(game["session_id"], str):
        raise ValueError("Invalid service response")

    try:
        uuid.UUID(game["session_id"])
    except (ValueError, AttributeError):
        raise ValueError("Invalid service response")

    if not isinstance(game["ships"], list):
        raise ValueError("Invalid service response")

    for ship in game["ships"]:
        if not isinstance(ship, dict):
            raise ValueError("Invalid service response")

        if "coordinates" not in ship:
            raise ValueError("Invalid service response")

        if not isinstance(ship["coordinates"], list):
            raise ValueError("Invalid service response")

    if not validate_fleet(
        [ship["coordinates"] for ship in game["ships"]]
    ):
        raise ValueError("Invalid fleet")

    return game


def create_match(service_a_url, service_b_url):
    try:
        game_a = create_game(service_a_url)
    except ValueError as error:
        if str(error) in ("Service timeout", "Invalid fleet"):
            return None, None, "B"
        raise

    try:
        game_b = create_game(service_b_url)
    except ValueError as error:
        if str(error) in ("Service timeout", "Invalid fleet"):
            return None, None, "A"
        raise

    return game_a, game_b, None


def make_shot(service_url, session_id):
    try:
        response = httpx.post(
            f"{service_url}/game/{session_id}/shot",
            timeout=1.0,
        )
        response.raise_for_status()

    except httpx.TimeoutException:
        raise ValueError("Service timeout")

    except httpx.HTTPError:
        raise ValueError("Service error")

    return response.json()


def send_opponent_shot(service_url, session_id, coordinate):
    try:
        response = httpx.post(
            f"{service_url}/game/{session_id}/opponent-shot",
            json={"coordinate": coordinate},
            timeout=1.0
        )
        response.raise_for_status()

    except httpx.TimeoutException:
        raise ValueError("Service timeout")

    except httpx.HTTPError:
        raise ValueError("Service error")

    return response.json()


def send_shot_result(service_url, session_id, result):
    try:
        response = httpx.post(
            f"{service_url}/game/{session_id}/shot/result",
            json={"result": result},
            timeout=1.0
        )
        response.raise_for_status()
    
    except httpx.TimeoutException:
        raise ValueError("Service timeout")
    
    except httpx.HTTPError:
        raise ValueError("Service error")

    return response.json()


def close_game(service_url, session_id):
    try:
        response = httpx.post(
            f"{service_url}/game/{session_id}/close",
            timeout=1.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        return None


def play_turn(
    shooter_url,
    shooter_session_id,
    defender_url,
    defender_session_id,
    defender_game,
    defender_hits,
):

    shot = make_shot(
        shooter_url,
        shooter_session_id,
    )

    
    if not isinstance(shot, dict) or "coordinate" not in shot:
        raise ValueError("Invalid service response")

    coordinate = shot["coordinate"]

    if (
        
        not isinstance(coordinate, str)
        or len(coordinate) < 2
        or coordinate[0] not in "ABCDEFGHIJ"
        or not coordinate[1:].isdigit()
        or not (1 <= int(coordinate[1:]) <= 10)
    ):
        raise ValueError("Invalid service response")


    result = send_opponent_shot(
        defender_url,
        defender_session_id,
        shot["coordinate"],
    )

    expected_result = get_expected_result(
        defender_game,
        shot["coordinate"],
        defender_hits,
    )

    if result.get("result") not in ("hit", "miss", "killed"):
        raise ValueError("Service returned invalid result")

    if result["result"] != expected_result:
        raise ValueError("Service returned incorrect result")

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


def get_expected_result(game, coordinate, hits):
    for ship in game["ships"]:
        ship_coordinates = set(ship["coordinates"])

        if coordinate in ship_coordinates:
            if ship_coordinates.issubset(hits | {coordinate}):
                return "killed"

            return "hit"

    return "miss"


def update_hits(hits, coordinate, result):
    if result in ("hit", "killed"):
        hits.add(coordinate)

    return hits


def play_match(service_a_url, service_b_url):
    game_a, game_b, winner = create_match(
        service_a_url,
        service_b_url,
    )

    if game_a is None:
        return winner

    hits_a = set()
    hits_b = set()

    current_shooter = random.choice(["A", "B"])

    while True:
        if current_shooter == "A":
            try:
                coordinate, result = play_turn(
                    service_a_url,
                    game_a["session_id"],
                    service_b_url,
                    game_b["session_id"],
                    game_b,
                    hits_b,
                )
            except ValueError as error:
                if str(error) in (
                    "Service timeout",
                    "Service error",
                    "Service returned incorrect result",
                    "Service returned invalid result",
                ):
                    winner = "B"
                    break
                raise

            print("A:", coordinate, result)
            
            hits_b = update_hits(hits_b, coordinate, result)

            if is_fleet_sunk(game_b, hits_b):
                winner = "A"
                break

        else:
            try:
                coordinate, result = play_turn(
                    service_b_url,
                    game_b["session_id"],
                    service_a_url,
                    game_a["session_id"],
                    game_a,
                    hits_a,
                )
            except ValueError as error:
                if str(error) in (
                    "Service timeout", 
                    "Service error"
                    "Service returned incorrect result",
                    "Service returned invalid result",
                    ):
                    winner = "A"
                    break
                raise

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