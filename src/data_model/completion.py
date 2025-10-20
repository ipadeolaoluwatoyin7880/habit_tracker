# src/data_model/completion.py
from datetime import datetime
from typing import Optional


class Completion:
    """Completion entity class representing a habit check-off event"""

    def __init__(self, timestamp: datetime, notes: Optional[str] = None, mood_score: Optional[int] = None):
        """
        Initialize a completion record

        Args:
            timestamp: When the habit was completed
            notes: Optional notes about the completion
            mood_score: Optional mood score (1-10)

        Raises:
            ValueError: If mood_score is not between 1-10 or timestamp is in future
        """
        self.timestamp = timestamp
        self.notes = notes
        self.mood_score = mood_score

        # Input validation
        if mood_score is not None and not (1 <= mood_score <= 10):
            raise ValueError("Mood score must be between 1 and 10")
        if timestamp > datetime.now():
            raise ValueError("Completion timestamp cannot be in the future")

    def to_dict(self) -> dict:
        """Convert completion to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes,
            'mood_score': self.mood_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Completion':
        """
        Create completion from dictionary

        Args:
            data: Dictionary with completion data

        Returns:
            Completion object
        """
        timestamp = datetime.fromisoformat(data['timestamp'])
        return cls(timestamp, data.get('notes'), data.get('mood_score'))

    def __repr__(self):
        """String representation for debugging"""
        mood_str = f", mood={self.mood_score}" if self.mood_score else ""
        notes_str = f", notes='{self.notes}'" if self.notes else ""
        return f"Completion(timestamp={self.timestamp}{notes_str}{mood_str})"

    def __eq__(self, other):
        """Check if two completions are equal"""
        if not isinstance(other, Completion):
            return False
        return (self.timestamp == other.timestamp and
                self.notes == other.notes and
                self.mood_score == other.mood_score)