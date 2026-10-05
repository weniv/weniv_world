class PathRecorder:
    def __init__(self):
        self.steps = []

    def record_step(self, location):
        self.steps.append(location)

    def retrace_steps(self):
        return list(reversed(self.steps))

path_recorder = PathRecorder()
path_recorder.record_step((0, 0))
for step in goto(4, 6):
    path_recorder.record_step(step)
pick()
for x, y in path_recorder.retrace_steps()[1:]:
    goto(x, y)
