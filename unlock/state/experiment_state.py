"""
This is the hardcoded app setup for the cVEP BCI experiment trials. It is for the cued phase only. There
are three different paradigms: 4-choice overt, 2-choice covert, and 2-choice gaze independent. In all three cases,
a template match based decoding approach will be used. These templates will be generated through an initial training
phase.

Training
cue target. present target for 5-12 seconds. provide qualitative feedback during training to indicate consistency of
templates. Only run as long as needed to get high accuracy templates or for a fixed (~5 min) period.

Testing
cue target. prep period. trial display (stop when confident or ~3 sec). feedback. rest.



"""
from unlock.state import UnlockState, TimerState


class ExperimentState(UnlockState):
    CueState = 0
    PrepState = 1
    TrialState = 2
    FeedbackState = 3
    RestState = 4

    def __init__(self):
        super(ExperimentState, self).__init__()
        self.state_durations = [0.5, 0.2, 2, 0.2, 0.5]
        self.state = -1
        self.state_change = False
        self.timer = TimerState(0)

    def get_state(self):
        if self.state_change:
            self.state_change = False
            return self.state

    def next(self):
        self.state = (self.state + 1) % len(self.state_durations)
        self.timer = TimerState(self.state_durations[self.state])
        self.timer.begin_timer()
        self.state_change = True

    def process_command(self, command):
        self.timer.update_timer(command.delta)
        if self.timer.is_complete():
            self.next()