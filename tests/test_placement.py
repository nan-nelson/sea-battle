from placement import (
    can_place_ship,
    choose_ship_candidate, 
    create_ship, 
    generate_fleet,
    get_ship_candidates, 
    is_ship_inside_field,
    score_ship_position, 
    validate_fleet
)


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

def test_ships_coordinates_must_have_valid_column():
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

    ships[0] = ["K1", "K2", "K3", "K4"]

    assert validate_fleet(ships) is False

def test_ships_coordinates_must_have_valid_row():
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

    ships[0] = ["A8", "A9", "A10", "A11"]

    assert validate_fleet(ships) is False

def test_ships_must_not_contain_duplicate_coordinates():
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

    ships[0] = ["A1", "A2", "A2", "A4"]

    assert validate_fleet(ships) is False

def test_ships_must_not_touch_by_corners():
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

    ships[1] = ["B5", "C5", "D5"]

    assert validate_fleet(ships) is False
    from placement import generate_fleet

def test_generate_fleet_returns_valid_fleet():
    ships = generate_fleet()

    assert validate_fleet(ships) is True
    from placement import create_ship


def test_create_horizontal_ship():
    ship = create_ship("A", 1, 4, True)

    assert ship == ["A1", "B1", "C1", "D1"]

def test_create_vertical_ship():
    ship = create_ship("A", 1, 4, False)

    assert ship == ["A1", "A2", "A3", "A4"]


def test_is_ship_inside_field():
    assert is_ship_inside_field(["A1", "A2", "A3", "A4"]) is True
    assert is_ship_inside_field(["A8", "A9", "A10", "A11"]) is False
    assert is_ship_inside_field(["H1", "I1", "J1",]) is True
    assert is_ship_inside_field(["I1", "J1", "K1"]) is False


def test_create_ship_candidate_is_valid():
    ship = create_ship("C", 5, 3, True)

    assert ship == ["C5", "D5", "E5"]
    assert is_ship_inside_field(ship) is True


def test_generate_fleet_creates_different_placements():
    first_fleet= generate_fleet()
    second_fleet = generate_fleet()

    assert first_fleet != second_fleet


def test_can_place_ship_rejects_touching_ships():
    occupied_cells = {"A1", "A2", "A3"}
    
    ship = ["B1", "B2"]

    assert can_place_ship(ship, occupied_cells) is False


def test_get_ship_candidates_returns_valid_ships():
    candidates = get_ship_candidates(4)

    assert candidates
    assert all(is_ship_inside_field(ship) for ship in candidates)
    assert all(len(ship) == 4 for ship in candidates)


def test_choose_ship_candidate_returns_valid_ship():
    occupied_cells = set ()

    ship = choose_ship_candidate(4, occupied_cells)

    assert ship is not None
    assert len(ship) == 4
    assert is_ship_inside_field(ship)


def test_score_ship_position_prefers_corner():
    corner_ship = ["A1", "A2", "A3", "A4"]
    center_ship = ["D4", "D5", "D6", "D7"]

    assert score_ship_position(corner_ship) > score_ship_position(center_ship)


def test_score_ship_position_prefers_border():
    border_ship = ["A4", "A5", "A6"]
    center_ship = ["D4", "D5", "D6"]

    assert score_ship_position(border_ship) > score_ship_position(center_ship)


def test_choose_ship_candidate_prefers_good_position():
    ship = choose_ship_candidate(4, set())

    assert score_ship_position(ship) == 16


def test_larger_ships_have_stronger_border_preference():
    border_ship_4 = ["A1", "A2", "A3", "A4"]
    border_ship_2= ["A5", "A6"]

    assert score_ship_position(border_ship_4) > score_ship_position(border_ship_2)