from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///eye_stats.db')
Session = sessionmaker(bind=engine)

class EyeState(Base):
    __tablename__ = 'eye_states'
    id = Column(Integer, primary_key=True)
    state = Column(String(10))
    duration = Column(Float)
    timestamp = Column(DateTime)

Base.metadata.create_all(engine)

class EyeTracker:
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.current_state = "open"
        self.start_time = datetime.now()
        self.session = Session()

    def update_state(self, ear):
        new_state = "closed" if ear < self.threshold else "open"
        if new_state != self.current_state:
            self._save_state()
            self.current_state = new_state
            self.start_time = datetime.now()

    def _save_state(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        record = EyeState(
            state=self.current_state,
            duration=duration,
            timestamp=self.start_time
        )
        self.session.add(record)
        self.session.commit()

    def get_stats(self):
        return {
            "state": self.current_state,
            "duration": round((datetime.now() - self.start_time).total_seconds(), 1)
        }
