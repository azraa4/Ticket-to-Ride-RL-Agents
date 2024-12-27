import tkinter as tk

class ModernSlider(tk.Scale):
    def __init__(self, parent, from_=0, to=100, length=200, orient=tk.HORIZONTAL, default_value=None, **kwargs):
        super().__init__(
            parent,
            from_=from_,  # Minimum value
            to=to,  # Maximum value
            length=length,  # Length of the slider
            orient=orient,  # Orientation (HORIZONTAL or VERTICAL)
            sliderlength=20,  # Length of the slider button
            troughcolor="#d9d9d9",  # Background color of the slider track
            background="#ae2907",  # Background color of the widget
            highlightthickness=2,  # Thickness of the border
            highlightbackground="#d9390a",  # Border color
            highlightcolor="white",  # Active border color
            fg="#ffffff",  # Foreground color (if labels are present)
            activebackground="#841804",  # Active background color (hover effect on slider button)
            bd=0,  # Border width
            **kwargs  # Additional parameters
        )
        if default_value is not None:
            self.set(default_value)
