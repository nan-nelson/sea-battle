EXPECTED_FLEET = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]


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

    return all(is_straight_ship(ship) for ship in ships)