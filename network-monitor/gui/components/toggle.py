"""
Custom toggle switch widget for PyQt5 applications.

Provides an animated toggle switch component that can be used as an alternative
to checkboxes for boolean settings like theme switching.
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QPaintEvent, QMouseEvent


class ToggleSwitch(QWidget):
    """
    Animated toggle switch widget.
    
    Provides a smooth animated toggle switch that changes color and position
    when clicked. Emits clicked signal with current state when toggled.
    """
    
    # Signal emitted when toggle state changes
    clicked = pyqtSignal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the toggle switch widget.
        
        Args:
            parent: Parent widget, if any
        """
        super().__init__(parent)
        
        # Configure widget appearance and behavior
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(QSize(50, 25))
        
        # Internal state
        self._checked = False
        self._offset = 2  # Position of the toggle circle
        
        # Animation for smooth toggle movement
        self.animation = QPropertyAnimation(self, b"offset", self)
        self.animation.setDuration(180)  # Animation duration in milliseconds

    def sizeHint(self) -> QSize:
        """
        Return the recommended size for this widget.
        
        Returns:
            Recommended size (50x25 pixels)
        """
        return QSize(50, 25)

    def isChecked(self) -> bool:
        """
        Check if the toggle switch is in the checked (on) state.
        
        Returns:
            True if checked, False otherwise
        """
        return self._checked

    def setChecked(self, value: bool) -> None:
        """
        Set the checked state of the toggle switch with animation.
        
        Args:
            value: True to check (turn on), False to uncheck (turn off)
        """
        self._checked = value
        
        # Calculate animation start and end positions
        start = self._offset
        end = self.width() - self.height() + 2 if value else 2
        
        # Configure and start animation
        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()
        
        # Trigger repaint
        self.update()

    def toggle(self) -> None:
        """
        Toggle the current state and emit the clicked signal.
        """
        self.setChecked(not self.isChecked())
        self.clicked.emit(self._checked)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events to toggle the switch.
        
        Args:
            event: Mouse press event
        """
        self.toggle()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the toggle switch with current state and position.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Choose background color based on checked state
        bg_color = QColor("#4cd137") if self._checked else QColor("#bdc3c7")  # Green if on, gray if off
        
        # Draw rounded rectangle background
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        
        # Draw white circle (toggle handle)
        painter.setBrush(QBrush(Qt.white))
        circle_size = self.height() - 4
        painter.drawEllipse(int(self._offset), 2, circle_size, circle_size)

    def getOffset(self) -> float:
        """
        Get the current offset position of the toggle handle.
        
        Returns:
            Current offset value
        """
        return self._offset

    def setOffset(self, value: float) -> None:
        """
        Set the offset position of the toggle handle and trigger repaint.
        
        Args:
            value: New offset value
        """
        self._offset = value
        self.update()

    # Property for animation system
    offset = pyqtProperty(float, fget=getOffset, fset=setOffset)