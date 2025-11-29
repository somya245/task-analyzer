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
        """Calculate urgency based on due date proximity"""
        today = timezone.now().date()
        
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
            
        days_until_due = (due_date - today).days
        
        if days_until_due < 0:
            return 1.0  # Past due - highest urgency
        elif days_until_due == 0:
            return 0.9  # Due today
        elif days_until_due <= 1:
            return 0.8  # Due tomorrow
        elif days_until_due <= 3:
            return 0.6  # Due in 3 days
        elif days_until_due <= 7:
            return 0.4  # Due in a week
        else:
            return max(0.1, 10.0 / days_until_due)  # Decreasing urgency
    
    def calculate_effort_score(self, estimated_hours):
        """Lower effort = higher score (quick wins)"""
        if estimated_hours <= 1:
            return 1.0  # Quick win
        elif estimated_hours <= 4:
            return 0.7  # Moderate effort
        elif estimated_hours <= 8:
            return 0.4  # Significant effort
        else:
            return max(0.1, 8.0 / estimated_hours)  # Large task
    
    def calculate_dependency_score(self, dependencies, all_tasks, current_task_id):
        """Tasks with more dependencies on them get higher scores"""
        if not dependencies:
            return 0.5  # Neutral score for no dependencies
        
        # Count how many tasks depend on this task
        blocking_count = 0
        current_task_id_str = str(current_task_id)
        
        for task in all_tasks:
            task_dependencies = task.get('dependencies', [])
            if current_task_id_str in task_dependencies:
                blocking_count += 1
        
        # Normalize to 0-1 scale
        return min(1.0, blocking_count * 0.3)
    
    def calculate_total_score(self, task, all_tasks):
        """Calculate overall priority score"""
        # Convert string date to date object if needed
        due_date = task['due_date']
        
        urgency_score = self.calculate_urgency_score(due_date)
        importance_score = task['importance'] / 10.0  # Normalize to 0-1 scale
        effort_score = self.calculate_effort_score(task['estimated_hours'])
        
        # Use task ID for dependency calculation
        task_id = task.get('id', 'temp_id')
        dependency_score = self.calculate_dependency_score(
            task.get('dependencies', []), all_tasks, task_id
        )
        
        # Calculate weighted total score
        total_score = (
            urgency_score * self.weights['urgency'] +
            importance_score * self.weights['importance'] +
            effort_score * self.weights['effort'] +
            dependency_score * self.weights['dependencies']
        )
        
        return round(total_score, 2)

def get_weights_for_strategy(strategy):
    """Get weight configuration for different sorting strategies"""
    strategies = {
        'smart': {'urgency': 0.4, 'importance': 0.3, 'effort': 0.2, 'dependencies': 0.1},
        'fastest': {'urgency': 0.2, 'importance': 0.2, 'effort': 0.5, 'dependencies': 0.1},
        'impact': {'urgency': 0.2, 'importance': 0.6, 'effort': 0.1, 'dependencies': 0.1},
        'deadline': {'urgency': 0.7, 'importance': 0.2, 'effort': 0.05, 'dependencies': 0.05},
    }
    return strategies.get(strategy, strategies['smart'])