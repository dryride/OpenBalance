class Session:
    def __init__(self, patient_metadata: dict = None):
        self.patient_metadata = patient_metadata or {}
        self.trials = []

    def add_trial(self, trial):
        self.trials.append(trial)