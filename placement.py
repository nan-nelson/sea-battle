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