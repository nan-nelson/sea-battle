from placement import validate_fleet


def test_valid_fleet():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8"],
        ["D8"],
        ["G8"],
        ["J10"],
    ]

    assert validate_fleet(ships) is True


def test_invalid_fleet_composition():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5", "E5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8", "B8"],
        ["D8", "E8"],
        ["G8"],
    ]

    assert validate_fleet(ships) is False

def test_ship_must_be_in_straight_line():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8"],
        ["D8"],
        ["G8"],
        ["J10"],
    ]

    ships[0] = ["A1", "A2", "B2", "B3"]

    assert validate_fleet(ships) is False

def test_ship_cells_must_be_continuous():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8"],
        ["D8"],
        ["G8"],
        ["J10"],
    ]

    ships[0] = ["A1", "A2", "A4", "A5"]

    assert validate_fleet(ships) is False
def test_ship_must_be_inside_field():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8"],
        ["D8"],
        ["G8"],
        ["J10"],
    ]

    ships[0] = ["A1", "A2", "A3", "A11"]

    assert validate_fleet(ships) is False
def test_ships_must_not_overlap():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8"],
        ["D8"],
        ["G8"],
        ["J10"],
    ]

    ships[1] = ["A4", "B4", "C4"]

    assert validate_fleet(ships) is False

def test_ships_must_not_touch_by_sides():
    ships = [
        ["A1", "A2", "A3", "A4"],
        ["C1", "D1", "E1"],
        ["G1", "G2", "G3"],
        ["C5", "D5"],
        ["G5", "G6"],
        ["I5", "I6"],
        ["A8"],
        ["D8"],
        ["G8"],
        ["J10"],
    ]

    ships[1] = ["B4", "C4", "D4"]

    assert validate_fleet(ships) is False