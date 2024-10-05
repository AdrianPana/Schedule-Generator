import utils
import sys
import time
from hc import apply_hill_climbing
from mcts import apply_monte_carlo_tree_search
import random

def run_hc_test(days, intervals, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs, name: str, n_trials: int = 10):
    wins = 0
    best = None
    total_restarts, total_states, total_time = 0, 0, 0
    random.seed(1999)
    
    for _ in range(n_trials):
        start_time = time.time()
        restarts, states, state, conflicts = apply_hill_climbing(days, intervals, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        if conflicts == 0: 
            wins += 1

        total_restarts += restarts
        total_states += states
        total_time += execution_time

        if not best or best.conflicts() > state.conflicts():
            best = state

    
    padding = ' ' * (10 - len(name))
    win_percentage = (wins / n_trials) * 100.
    print(f"Success rate for {name}: {padding}{wins} / {n_trials} ({win_percentage:.2f}%)")
    print(f"Average number of restarts: {' ':8}{(total_restarts / n_trials):.2f}")
    print(f"Average number of states: {' ':>14}{total_states / n_trials:.2f}")
    print(f"Average execution time: {' ':>17}{total_time / n_trials:.2f}")

    return best.schedule

def run_mcts_test(days, intervals, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs, name: str, n_trials: int = 10):
    wins = 0
    best = None
    total_states, total_time = 0, 0
    random.seed(1999)
    
    for _ in range(n_trials):
        start_time = time.time()
        states, state, conflicts = apply_monte_carlo_tree_search(days, intervals, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        if conflicts == 0: 
            wins += 1

        total_states += states
        total_time += execution_time

        if not best or best.conflicts() > state.conflicts():
            best = state

    
    padding = ' ' * (10 - len(name))
    win_percentage = (wins / n_trials) * 100.
    print(f"Success rate for {name}: {padding}{wins} / {n_trials} ({win_percentage:.2f}%)")
    print(f"Average number of states: {' ':>14}{total_states / n_trials:.2f}")
    print(f"Average execution time: {' ':>17}{total_time / n_trials:.2f}")

    return best.schedule


def interval_to_index(interval):
    margins = interval.split("-")
    left = (int(margins[0]) - 8) // 2
    right = (int(margins[1]) - 8) // 2
    return left, right

def init_room():
    return [[1 for _ in range(INTERVALS)] for _ in range(DAYS)]


def get_prof_prefs(info):
    prefs = [[1 for _ in range(INTERVALS)] for _ in range(DAYS)]

    day_prefs = info["Constrangeri"][:DAYS]
    interval_prefs = info["Constrangeri"][DAYS:]

    for i, day in enumerate(day_prefs):
        if day[0] == '!':
            for j in range(INTERVALS):
                prefs[i][j] = 0

    for interval in interval_prefs:
        if interval[0] == '!':
            left, right = interval_to_index(interval[1:])
            for i in range(DAYS):
                for j in range(left, right):
                    prefs[i][j] = 0

    return prefs

def schedule_to_dict(schedule):
    DAY_LABELS = ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri']
    INTERVAL_LABELS = [(8,10), (10,12), (12,14), (14,16), (16,18), (18,20)]

    dict = {}
    for i in range(DAYS):
        day_dict = {}
        for j in range(INTERVALS):
            day_dict[INTERVAL_LABELS[j]] = schedule[i][j]
        dict[DAY_LABELS[i]] = day_dict

    return dict


if __name__ == "__main__":

    mode = 0
    global DAYS
    global INTERVALS

    if len(sys.argv) != 3:
        print("Usage: python3 orar.py hc/mcts input_file")
        sys.exit()

    if sys.argv[1] == "hc":
        mode = 1
    elif sys.argv[1] == "mcts":
        mode = 2
    else:
        print("Invalid algorithm")
        sys.exit()

    input_file = sys.argv[2]
    input_name = f'inputs/{input_file}.yaml'
    output_name = f'outputs/{input_file}.txt'
    dict = utils.read_yaml_file(input_name)

    INTERVALS = len(dict["Intervale"])
    DAYS = len(dict["Zile"])

    # global result state
    schedule = [[{room: None for room in dict["Sali"].keys()} for _ in range(INTERVALS)] for _ in range(DAYS)]

    # easy way to access teacher posibilities
    profs_prefs = {prof: get_prof_prefs(dict["Profesori"][prof]) for prof in dict["Profesori"].keys()}
    prof_classes = {prof: dict["Profesori"][prof]["Materii"] for prof in dict["Profesori"].keys()}
    prof_jobs = {prof: 0 for prof in dict["Profesori"].keys()}

    # easy room state access
    rooms = {room: (val["Materii"], int(val["Capacitate"]), init_room()) for room, val in dict["Sali"].items()}

    classes = {key: int(value) for key,value in dict["Materii"].items()}

    result = {}
    if mode == 1:
        # Commented lines are for testing with statistics
        # result = run_hc_test(DAYS, INTERVALS, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs, input_file)
        _, _, result_state, _ = apply_hill_climbing(DAYS, INTERVALS, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs)
        result = result_state.schedule
    elif mode == 2:
        # result = run_mcts_test(DAYS, INTERVALS, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs, input_file)
        _, result_state, _ = apply_monte_carlo_tree_search(DAYS, INTERVALS, schedule, classes, profs_prefs, rooms, prof_classes, prof_jobs)
        result = result_state.schedule

    with open(output_name, "w") as file:
        print(utils.pretty_print_timetable(schedule_to_dict(result), input_name), file=file)

    
 