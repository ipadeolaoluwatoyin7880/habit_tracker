from datetime import datetime


class Completion:
    def __init__(self, notes: str = "", mood_score: int = None):
        self.timestamp = datetime.now()
        self.notes = notes
        self.mood_score = mood_score

        # Validate mood score
        if mood_score is not None and (mood_score < 1 or mood_score > 10):
            raise ValueError("Mood score must be between 1 and 10")

    def __repr__(self):
        mood_str = f", mood: {self.mood_score}" if self.mood_score else ""
        return f"Completion({self.timestamp.strftime('%Y-%m-%d %H:%M')}{mood_str})"

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'notes': self.notes,
            'mood_score': self.mood_score
        }

    @classmethod
    def from_dict(cls, data):
        completion = cls(notes=data.get('notes'), mood_score=data.get('mood_score'))
        completion.timestamp = data['timestamp']
        return completion