from state import State
import random

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

def apply_hill_climbing(days, intervals, schedule, classes, prof_prefs, rooms, prof_classes, prof_jobs):
    global DAYS, INTERVALS
    DAYS, INTERVALS = days, intervals

    State.DAYS = DAYS
    State.INTERVALS = INTERVALS
    state = State(schedule, classes, prof_prefs, rooms, prof_classes, prof_jobs, 0)

    restarts, states, result = hill_climbing(state)

    return restarts, states, result, result.conflicts()

def hill_climbing(initial: State, max_iters: int = 2500, max_restarts: int = 10):
    iters, states = 0, 0
    restarts = 0
    state = initial.clone()
    random.seed()
    is_best = False
    best = None

    
    while restarts < max_restarts:
        restarts += 1

        iters = 0
        while iters < max_iters:
            iters += 1

            next_states = state.get_next_states()
            states += len(next_states)

            if len(next_states) == 0:
                break

            state = random.choice(next_states)
        
            if state.is_final():
                if not best or state.conflicts() < best.conflicts():
                    best = state
                if state.conflicts() == 0:
                    is_best = True
                break
            
        if is_best:
            break
        else:
            state = initial.clone()
            random.seed(random.random())
    
    return restarts, states, best