from copy import deepcopy, copy

class State:
    def __init__(
        self, 
        schedule,
        classes,
        prefs,
        rooms,
        prof_classes,
        prof_jobs,
        conflicts: int | None = None,
    ) -> None:
        
        self.schedule = schedule
        self.classes = classes
        self.prefs = prefs
        self.rooms = rooms
        self.prof_classes = prof_classes
        self.prof_jobs = prof_jobs
        self.nconflicts = conflicts if conflicts is not None \
            else State.__compute_conflicts(self.size, self.board)

    def clone(self):
        return State(deepcopy(self.schedule), copy(self.classes), deepcopy(self.prefs), 
                     deepcopy(self.rooms), deepcopy(self.prof_classes), copy(self.prof_jobs), self.nconflicts) 

    def conflicts(self):
        return self.nconflicts

    def is_final(self) -> bool:
        for students in self.classes.values():
            if students > 0:
                return False

        return True
    
    def get_next_class(self):
        min_key = None
        min_val = 0
        for key, val in self.classes.items():
            if val > 0 and (not min_key or min_val > val):
                min_key = key
                min_val = val

        return min_key
                

    def book_class(self, next_class, room, prof, day, interval):
        new_schedule = deepcopy(self.schedule)
        new_schedule[day][interval][room] = (prof, next_class)
        classes = deepcopy(self.classes)
        classes[next_class] -= self.rooms[room][1]
        new_rooms = deepcopy(self.rooms)
        new_rooms[room][2][day][interval] = 0
        new_prefs = deepcopy(self.prefs)
        new_jobs = copy(self.prof_jobs)
        new_jobs[prof] += 1
        conflict = 0
        if new_prefs[prof][day][interval] == 0:
            conflict = 1
        new_prefs[prof][day][interval] = -1
        return State(new_schedule, classes, new_prefs, new_rooms, self.prof_classes, new_jobs, self.nconflicts + conflict)


    def get_next_states(self):
        result = []
        global no_conflicts 
        no_conflicts = False
        
        prior_conflicts = self.nconflicts

        next_class = self.get_next_class()

        for room in self.rooms.keys():
            if next_class in self.rooms[room][0]:
                for prof, val in self.prof_classes.items():
                    if not next_class in val or self.prof_jobs[prof] >= 7:
                        continue

                    for i in range(State.DAYS):
                        for j in range(State.INTERVALS):
                            if self.prefs[prof][i][j] >= 0 and self.rooms[room][2][i][j] > 0:
                                new_state = self.book_class(next_class, room, prof, i, j)
                                if prior_conflicts - new_state.nconflicts == 0:
                                    if not no_conflicts:
                                        no_conflicts = True
                                        result = []
                                    result.append(new_state)
                                elif not no_conflicts:
                                    result.append(new_state)
        return result
    
    def get_available_actions(self, no_conflicts=True):
        result = []
        threshold = 1 if no_conflicts else 0
        next_class = self.get_next_class()

        for room in self.rooms.keys():
            if next_class in self.rooms[room][0]:
                for prof, val in self.prof_classes.items():
                    if not next_class in val or self.prof_jobs[prof] >= 7:
                        continue

                    for i in range(State.DAYS):
                        for j in range(State.INTERVALS):
                            if self.prefs[prof][i][j] >= threshold and self.rooms[room][2][i][j] > 0:
                                result.append((i, j, next_class, room, prof))
        return result
        
Result = tuple[bool, int, int, State]
