import random
from state import State
from math import sqrt, log, exp

N = 'N'
Q = 'Q'
STATE = 'state'
PARENT = 'parent'
ACTIONS = 'actions'
bestBEST = None

def init_node(state, parent = None):
    return {N: 0, Q: 0, STATE: state, PARENT: parent, ACTIONS: {}}

CP = 1.0 / sqrt(2.0)

def select_action(node, c = CP):

    N_node = node[N]
    exp = lambda Q_a, N_a: Q_a / N_a  +  c * sqrt(2 * log(N_node) / N_a)
    return max(node[ACTIONS].items(), key=lambda action: exp(action[1][Q], action[1][N]))[0]
    
def compute_reward(conflicts):
    return 1 - (1 / 1 + exp(-conflicts))

def apply_monte_carlo_tree_search(days, intervals, schedule, classes, prof_prefs, rooms, prof_classes, prof_jobs):
    global DAYS, INTERVALS
    DAYS, INTERVALS = days, intervals

    State.DAYS = DAYS
    State.INTERVALS = INTERVALS
    state = State(schedule, classes, prof_prefs, rooms, prof_classes, prof_jobs, 0)

    result, states = mcts(state, 6900)

    if not result:
        result = state
    return states, result, result.conflicts()

def mcts(state0, budget):

    tree = init_node(state0, None)
    best = None
    found_best = False
    states = 0
    no_conflicts_possible = True
    random.seed()

    for i in range(budget):

        if found_best:
            break

        node = tree

        while not node[STATE].is_final():
            avail = node[STATE].get_available_actions(no_conflicts_possible)

            unexplored = False
            for act in avail:
                if act not in node[ACTIONS]:
                    unexplored = True
                    break

            if unexplored or (best and node[STATE].conflicts() >= best.conflicts()):
                break

            if not unexplored and node == tree:
                no_conflicts_possible = False

            new_action = select_action(node)
            node = node[ACTIONS][new_action]
        
        if best and node[STATE].conflicts() >= best.conflicts():
            i -= 1
            continue

        available_actions = node[STATE].get_available_actions(no_conflicts_possible)
        states += len(available_actions)
        available_actions = list(filter(lambda act: act not in node[ACTIONS], available_actions))

        if not node[STATE].is_final() and len(available_actions) > 0:
            chosen_action = random.choice(available_actions)
            day, interval, _class, room, prof = chosen_action
            new_state = node[STATE].book_class(_class, room, prof, day, interval)
            new_node = init_node(new_state, node)
            node[ACTIONS][chosen_action] = new_node
            node = new_node

        state = node[STATE]
        while not state.is_final():
            sim_actions = state.get_available_actions(no_conflicts_possible)
            if len(sim_actions) == 0:
                break
            day, interval, _class, room, prof = random.choice(sim_actions)
            state = state.book_class(_class, room, prof, day, interval)

        if not state.is_final():
            reward = 0
        else:
            reward = compute_reward(state.conflicts())
            if not best or best.nconflicts > state.conflicts():
                best = state
                if best.nconflicts == 0:
                    found_best = True
                    break

        while node:
            node[N] += 1
            node[Q] += reward
            node = node[PARENT]

    return (best, states)