from datetime import date
from django.utils import timezone

class TaskScorer:
    def __init__(self, weights=None):
        self.weights = weights or {
            'urgency': 0.4,
            'importance': 0.3,
            'effort': 0.2,
            'dependencies': 0.1
        }
    
    def calculate_urgency_score(self, due_date):
        today = timezone.now().date()
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        days_until_due = (due_date - today).days
        if days_until_due < 0:
            return 1.0
        elif days_until_due == 0:
            return 0.9
        elif days_until_due <= 1:
            return 0.8
        elif days_until_due <= 3:
            return 0.6
        elif days_until_due <= 7:
            return 0.4
        else:
            return max(0.1, 10.0 / days_until_due)
    
    def calculate_effort_score(self, estimated_hours):
        if estimated_hours <= 1:
            return 1.0
        elif estimated_hours <= 4:
            return 0.7
        elif estimated_hours <= 8:
            return 0.4
        else:
            return max(0.1, 8.0 / estimated_hours)
    
    def calculate_dependency_score(self, dependencies, all_tasks, current_task_id):
        if not dependencies:
            return 0.5
        blocking_count = 0
        current_task_id_str = str(current_task_id)
        for task in all_tasks:
            task_dependencies = task.get('dependencies', [])
            if current_task_id_str in task_dependencies:
                blocking_count += 1
        return min(1.0, blocking_count * 0.3)
    
    def calculate_total_score(self, task, all_tasks):
        due_date = task['due_date']
        urgency_score = self.calculate_urgency_score(due_date)
        importance_score = task['importance'] / 10.0
        effort_score = self.calculate_effort_score(task['estimated_hours'])
        task_id = task.get('id', 'temp_id')
        dependency_score = self.calculate_dependency_score(
            task.get('dependencies', []), all_tasks, task_id
        )
        total_score = (
            urgency_score * self.weights['urgency'] +
            importance_score * self.weights['importance'] +
            effort_score * self.weights['effort'] +
            dependency_score * self.weights['dependencies']
        )
        return round(total_score, 2)

def get_weights_for_strategy(strategy):
    strategies = {
        'smart': {'urgency': 0.4, 'importance': 0.3, 'effort': 0.2, 'dependencies': 0.1},
        'fastest': {'urgency': 0.2, 'importance': 0.2, 'effort': 0.5, 'dependencies': 0.1},
        'impact': {'urgency': 0.2, 'importance': 0.6, 'effort': 0.1, 'dependencies': 0.1},
        'deadline': {'urgency': 0.7, 'importance': 0.2, 'effort': 0.05, 'dependencies': 0.05},
    }
    return strategies.get(strategy, strategies['smart'])
