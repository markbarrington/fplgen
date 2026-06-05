import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class FplreviewSourceTable:
    fieldnames: list
    rows: list


@dataclass(frozen=True)
class FplreviewProjection:
    player_id: int
    name: str
    team: int
    team_name: str
    element_type: int
    now_cost: int
    sellprice: int
    weekly_points: dict
    thisweekpoints: float
    lookaheadpoints: float
    ppg: float
    total_points: float
    tsp: float


def read_fplreview_csv(filename):
    with open(filename, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            raise ValueError("fplreview CSV has no header row")
        return FplreviewSourceTable(fieldnames=reader.fieldnames, rows=list(reader))


def fplreview_gameweek_columns(fieldnames, gameweek, forecastweeks):
    columns = {}
    missing = []
    for week in range(gameweek, gameweek + forecastweeks):
        candidates = [
            "%s_Pts" % week,
            "GW%s_Pts" % week,
            "GW%s Pts" % week,
            "%s_PTS" % week,
            "GW%s_PTS" % week,
        ]
        found = None
        for candidate in candidates:
            if candidate in fieldnames:
                found = candidate
                break
        if found is None:
            missing.append("%s_Pts" % week)
        else:
            columns[week - gameweek + 1] = found

    if missing:
        raise ValueError(
            "Missing required fplreview gameweek columns: %s" % ", ".join(missing)
        )

    return columns


def fplreview_price(value):
    price = float(value)
    if price <= 20:
        price *= 10
    return int(round(price))


def fplreview_position(value):
    position = str(value).strip().lower()
    positions = {
        "1": 1,
        "gk": 1,
        "gkp": 1,
        "goalkeeper": 1,
        "2": 2,
        "def": 2,
        "defender": 2,
        "3": 3,
        "mid": 3,
        "midfielder": 3,
        "4": 4,
        "fwd": 4,
        "for": 4,
        "forward": 4,
    }
    if position not in positions:
        raise ValueError("Unknown fplreview position: %s" % value)
    return positions[position]


def resolve_fplreview_team(value, team_map):
    updated_team_map = {str(team_id): team_name for team_id, team_name in team_map.items()}
    team_name = str(value).strip()
    for existing_id, existing_name in updated_team_map.items():
        if existing_name.lower() == team_name.lower():
            return int(existing_id), existing_name, updated_team_map

    next_id = max(int(existing_id) for existing_id in updated_team_map.keys()) + 1
    updated_team_map[str(next_id)] = team_name
    return next_id, team_name, updated_team_map


def normalize_fplreview_rows(rows, fieldnames, gameweek, forecastweeks, team_map):
    required = ["Pos", "ID", "Name", "BV", "SV", "Team"]
    missing = [field for field in required if field not in fieldnames]
    if missing:
        raise ValueError("Missing required fplreview columns: %s" % ", ".join(missing))

    point_columns = fplreview_gameweek_columns(fieldnames, gameweek, forecastweeks)
    working_team_map = {str(team_id): team_name for team_id, team_name in team_map.items()}
    projections = []
    for row in rows:
        projection, working_team_map = normalize_fplreview_player(
            row,
            point_columns,
            forecastweeks,
            working_team_map,
        )
        projections.append(projection)
    return projections, working_team_map


def normalize_fplreview_player(row, point_columns, forecastweeks, team_map):
    player_id = int(row["ID"])
    element_type = fplreview_position(row["Pos"])
    team, team_name, updated_team_map = resolve_fplreview_team(row["Team"], team_map)
    now_cost = fplreview_price(row["BV"])
    sellprice = fplreview_price(row["SV"])

    weekly_points = {}
    lookahead = 0
    for week, column in point_columns.items():
        points = float(row[column])
        weekly_points[week] = points
        lookahead += points

    projection = FplreviewProjection(
        player_id=player_id,
        name=row["Name"],
        team=team,
        team_name=team_name,
        element_type=element_type,
        now_cost=now_cost,
        sellprice=sellprice,
        weekly_points=weekly_points,
        thisweekpoints=weekly_points[1],
        lookaheadpoints=lookahead,
        ppg=lookahead / float(forecastweeks),
        total_points=lookahead,
        tsp=lookahead,
    )
    return projection, updated_team_map


def prepare_scorer_players(projections, forecastweeks, playertypes):
    return [
        prepare_scorer_player(projection, forecastweeks, playertypes)
        for projection in projections
    ]


def prepare_scorer_player(projection, forecastweeks, playertypes):
    player = {
        "id": projection.player_id,
        "code": projection.player_id,
        "second_name": projection.name,
        "web_name": projection.name,
        "team": projection.team,
        "team_name": projection.team_name,
        "element_type": projection.element_type,
        "type_name": playertypes[projection.element_type - 1],
        "now_cost": projection.now_cost,
        "sellprice": projection.sellprice,
        "status": "a",
        "picked": False,
        "minutes": 0,
        "total_points": projection.total_points,
        "tsp": projection.tsp,
        "home": 0,
        "away": 0,
        "homegames": 0,
        "awaygames": 0,
        "otherteams": ["NONE"] * forecastweeks,
        "thisweekpoints": projection.thisweekpoints,
        "lookaheadpoints": projection.lookaheadpoints,
        "ppg": projection.ppg,
    }

    for week, points in projection.weekly_points.items():
        player[str(week)] = points

    return player


def load_fplreview_players(filename, gameweek, forecastweeks, team_map, playertypes):
    source = read_fplreview_csv(filename)
    projections, updated_team_map = normalize_fplreview_rows(
        source.rows,
        source.fieldnames,
        gameweek,
        forecastweeks,
        team_map,
    )
    return prepare_scorer_players(projections, forecastweeks, playertypes), updated_team_map


def format_playerkeydata_lines(loaded_players, forecastweeks, playertype):
    lines = []
    for player in loaded_players:
        playerdata = player["second_name"]
        playerdata += "," + str(player["total_points"])
        playerdata += "," + str(player["minutes"])
        playerdata += "," + str(player["tsp"])
        playerdata += "," + str(player["now_cost"])
        playerdata += "," + player["team_name"]
        playerdata += "," + playertype[str(player["element_type"])]
        playerdata += "," + str(player["lookaheadpoints"])
        playerdata += "," + str(player["thisweekpoints"])
        playerdata += "," + str(player["ppg"])
        for week in range(1, forecastweeks + 1):
            playerdata += "," + str(player[str(week)])
        lines.append(playerdata)
    return lines
