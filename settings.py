class Settings:
    AVAILABLE_RESOLUTIONS = [
        (1280, 720),
        (1600, 900),
        (1920, 1080),
    ]

    def __init__(self):
        self.resolution_index = 2
        self.pending_resolution_index = 2
        self.screen_width = self.AVAILABLE_RESOLUTIONS[2][0]
        self.screen_height = self.AVAILABLE_RESOLUTIONS[2][1]
        self.windowed_fullscreen = True

    def apply_resolution(self, index: int):
        """Applies the resolution at the given index from AVAILABLE_RESOLUTIONS."""
        self.resolution_index = index
        self.pending_resolution_index = index
        self.screen_width = self.AVAILABLE_RESOLUTIONS[index][0]
        self.screen_height = self.AVAILABLE_RESOLUTIONS[index][1]

    def select_pending_resolution(self, index: int):
        """Selects a resolution to preview without applying it yet."""
        self.pending_resolution_index = index

    def apply_pending_resolution(self):
        """Applies the currently pending resolution selection."""
        self.apply_resolution(self.pending_resolution_index)

    def get_resolution_label(self, index: int) -> str:
        """Returns a display string for the resolution at the given index."""
        width, height = self.AVAILABLE_RESOLUTIONS[index]
        return f"{width} x {height}"
