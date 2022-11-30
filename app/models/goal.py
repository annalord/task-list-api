from app import db


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    tasks = db.relationship("Task", back_populates="goal", lazy=True)

    def to_dict(self):
        return {
            "id" : self.goal_id,
            "title" : self.title, 
        }

    
    @classmethod
    def from_dict(cls, dict_data):
        return cls(
            title = dict_data["title"],
        )

    def task_ids(self): 
        return [task.task_id for task in self.tasks]