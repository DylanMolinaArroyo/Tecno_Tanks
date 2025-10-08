class Button():
    def __init__(self, pos, text_input, font, base_color, hovering_color):
        """
        Initializes a UI button with text and color states.

        Args:
            pos (tuple): (x, y) position for the button center.
            text_input (str): Text to display on the button.
            font (pygame.font.Font): Font object for rendering text.
            base_color (tuple): RGB color for normal state.
            hovering_color (tuple): RGB color for hover state.
        """

        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """
        Draws the button text on the given screen surface.

        Args:
            screen (pygame.Surface): Surface to draw the button on.
        """
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        """
        Checks if a given position collides with the button.

        Args:
            position (tuple): (x, y) position to check.

        Returns:
            bool: True if position is over the button, False otherwise.
        """
            
        if self.text_rect.collidepoint(position):
            return True
        return False

    def changeColor(self, position):
        """
        Changes the button text color based on hover state.

        Args:
            position (tuple): (x, y) position to check for hover.
        """
        
        if self.text_rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
