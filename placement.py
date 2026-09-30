import random

EXPECTED_FLEET = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]


def is_valid_coordinate(coordinate):
    if not coordinate or coordinate[0] not in "ABCDEFGHIJ":
        return False

    try:
        row = int(coordinate[1:])
    except ValueError:
        return False

    return 1 <= row <= 10


def get_neighbours(coordinate):
    column = ord(coordinate[0]) - ord("A")
    row = int(coordinate[1:]) - 1

    neighbours = []

    for column_offset in (-1, 0, 1):
        for row_offset in (-1, 0, 1):
            if column_offset == 0 and row_offset == 0:
                continue

            neighbour_column = column + column_offset
            neighbour_row = row + row_offset

            if 0 <= neighbour_column < 10 and 0 <= neighbour_row < 10:
                neighbours.append(
                    chr(ord("A") + neighbour_column) + str(neighbour_row + 1)
                )

    return neighbours


def is_straight_ship(ship):
    if len(ship) <= 1:
        return True

    columns = [coordinate[0] for coordinate in ship]
    rows = [int(coordinate[1:]) for coordinate in ship]

    same_column = len(set(columns)) == 1
    same_row = len(set(rows)) == 1

    if not (same_column or same_row):
        return False

    if same_column:
        rows.sort()
        return rows == list(range(rows[0], rows[0] + len(rows)))

    columns.sort()
    return columns == [
        chr(ord(columns[0]) + i)
        for i in range(len(columns))
    ]


def validate_fleet(ships):
    ship_sizes = sorted(len(ship) for ship in ships)

    if ship_sizes != EXPECTED_FLEET:
        return False

    occupied_cells = set()

    for ship in ships:
        if not all(is_valid_coordinate(coordinate) for coordinate in ship):
            return False

        if not is_straight_ship(ship):
            return False

        for coordinate in ship:
            if coordinate in occupied_cells:
                return False

            occupied_cells.add(coordinate)

    for ship in ships:
        for coordinate in ship:
            for neighbour in get_neighbours(coordinate):
                if neighbour in occupied_cells and neighbour not in ship:
                    return False

    return True

FIELD_COLUMNS = "ABCDEFGHIJ"
FIELD_ROWS = range(1, 11)


def create_ship(start_column, start_row, size, horizontal):
    ship = []

    for i in range(size):
        if horizontal:
            column = chr(ord(start_column) + i)
            row = start_row
        else:
            column = start_column
            row = start_row + i

        ship.append(f"{column}{row}")

    return ship


def is_ship_inside_field(ship):
    return all(is_valid_coordinate(coordinate) for coordinate in ship)


def can_place_ship(ship, occupied_cells):
    for coordinate in ship:
        if coordinate in occupied_cells:
            return False

        for neighbour in get_neighbours(coordinate):
            if neighbour in occupied_cells:
                return False

    return True


def get_ship_candidates(size):
    candidates = []

    for column in FIELD_COLUMNS:
        for row in FIELD_ROWS:
            for horizontal in (True, False):
                ship = create_ship(column, row, size, horizontal)

                if is_ship_inside_field(ship):
                    candidates.append(ship)

    return candidates


def score_ship_position(ship):
    size = len(ship)
    score = 0

    if size >= 4:
        border_score = 3
        corner_bonus = 4
    elif size == 3:
        border_score = 2
        corner_bonus = 3
    elif size == 2:
        border_score = 1
        corner_bonus = 1
    else:
        border_score = 0
        corner_bonus = 0

    for coordinate in ship:
        column = coordinate[0]
        row = int(coordinate[1:])

        if column in ("A", "J") or row in (1, 10):
            score += border_score

        if column in ("A", "J") and row in (1, 10):
            score += corner_bonus

    return score


def choose_ship_candidate(size, occupied_cells):
    candidates = get_ship_candidates(size)

    valid_candidates = [
        ship
        for ship in candidates
        if can_place_ship(ship, occupied_cells)
    ]

    if not valid_candidates:
        return None

    best_score = max(score_ship_position(ship) for ship in valid_candidates)

    score_threshold = best_score - 2

    good_candidates = [
        ship
        for ship in valid_candidates
        if score_ship_position(ship) >= score_threshold
    ]

    return random.choice(good_candidates)

def generate_fleet():
    for _ in range(100):
        ships = []
        occupied_cells = set()

        for size in reversed(EXPECTED_FLEET):
            ship = choose_ship_candidate(size, occupied_cells)

            if ship is None:
                break

            ships.append(ship)
            occupied_cells.update(ship)

            if validate_fleet(ships):
                return ships
    raise RuntimeError("Failed to generate a valid fleet")