import numpy as np

class Trial:
    def __init__(self, raw_data: np.ndarray, sample_rate: float, channel_names: list, metadata: dict = None):
        """
        raw_data: 2D Numpy Array (Samples x Kanäle)
        channel_names: z.B. ['F1', 'F2', 'F3', 'F4'] oder bei OpenBalance bis 'F16'
        """
        self.raw_data = raw_data
        self.sample_rate = sample_rate
        self.channel_names = channel_names
        self.metadata = metadata or {}
        
        self.filtered_data = None  # Wird später durch processing befüllt
        self.parameters = {}       # Nimmt später COP, WD, ST etc. auf