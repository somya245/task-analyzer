from django.test import TestCase
from datetime import date, timedelta
from django.utils import timezone
from .scoring import TaskScorer, get_weights_for_strategy

class TaskScoringTests(TestCase):
    def setUp(self):
        self.scorer = TaskScorer()
        self.today = timezone.now().date()
        self.sample_tasks = [
            {'id': '1', 'title': 'Urgent Task', 'due_date': self.today, 'estimated_hours': 2, 'importance': 9, 'dependencies': []},
            {'id': '2', 'title': 'Future Task', 'due_date': self.today + timedelta(days=10), 'estimated_hours': 8, 'importance': 6, 'dependencies': []},
            {'id': '3', 'title': 'Bug Fix', 'due_date': self.today + timedelta(days=30), 'estimated_hours': 2, 'importance': 9, 'dependencies': []},
            {'id': '4', 'title': 'Documentation', 'due_date': self.today + timedelta(days=5), 'estimated_hours': 4, 'importance': 6, 'dependencies': []}
        ]
    
    def test_urgency_score_past_due(self):
        past_date = self.today - timedelta(days=1)
        score = self.scorer.calculate_urgency_score(past_date)
        self.assertEqual(score, 1.0)
    
    def test_urgency_score_due_today(self):
        score = self.scorer.calculate_urgency_score(self.today)
        self.assertEqual(score, 0.9)
    
    def test_urgency_score_due_tomorrow(self):
        tomorrow = self.today + timedelta(days=1)
        score = self.scorer.calculate_urgency_score(tomorrow)
        self.assertEqual(score, 0.8)
    
    def test_urgency_score_far_future(self):
        future_date = self.today + timedelta(days=100)
        score = self.scorer.calculate_urgency_score(future_date)
        self.assertLess(score, 0.2)
        self.assertGreaterEqual(score, 0.1)
    
    def test_effort_score_quick_win(self):
        score = self.scorer.calculate_effort_score(1)
        self.assertEqual(score, 1.0)
    
    def test_effort_score_moderate(self):
        score = self.scorer.calculate_effort_score(4)
        self.assertEqual(score, 0.7)
    
    def test_effort_score_significant(self):
        score = self.scorer.calculate_effort_score(8)
        self.assertEqual(score, 0.4)
    
    def test_effort_score_large_task(self):
        score = self.scorer.calculate_effort_score(20)
        self.assertLess(score, 0.5)
        self.assertGreaterEqual(score, 0.1)
    
    def test_dependency_score_no_dependencies(self):
        score = self.scorer.calculate_dependency_score([], self.sample_tasks, '1')
        self.assertEqual(score, 0.5)
    
    def test_dependency_score_with_blockers(self):
        tasks_with_deps = [
            {'id': '1', 'title': 'Task 1', 'due_date': self.today, 'estimated_hours': 2, 'importance': 5, 'dependencies': ['base-task']},
            {'id': '2', 'title': 'Task 2', 'due_date': self.today, 'estimated_hours': 2, 'importance': 5, 'dependencies': ['base-task']},
            {'id': 'base-task', 'title': 'Base Task', 'due_date': self.today, 'estimated_hours': 1, 'importance': 8, 'dependencies': []}
        ]
        score = self.scorer.calculate_dependency_score([], tasks_with_deps, 'base-task')
        self.assertGreaterEqual(score, 0.5)
    
    def test_total_score_bounds(self):
        task = self.sample_tasks[0]
        score = self.scorer.calculate_total_score(task, self.sample_tasks)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_total_score_high_priority_task(self):
        high_priority = {
            'id': 'hp1', 'title': 'Critical', 'due_date': self.today - timedelta(days=1),
            'estimated_hours': 1, 'importance': 10, 'dependencies': []
        }
        score = self.scorer.calculate_total_score(high_priority, [high_priority])
        self.assertGreater(score, 0.8)
    
    def test_total_score_low_priority_task(self):
        low_priority = {
            'id': 'lp1', 'title': 'Nice to have', 'due_date': self.today + timedelta(days=365),
            'estimated_hours': 40, 'importance': 1, 'dependencies': []
        }
        score = self.scorer.calculate_total_score(low_priority, [low_priority])
        self.assertLess(score, 0.3)
    
    def test_strategy_weights_smart(self):
        weights = get_weights_for_strategy('smart')
        self.assertEqual(weights['urgency'], 0.4)
        self.assertEqual(weights['importance'], 0.3)
        self.assertEqual(weights['effort'], 0.2)
        self.assertEqual(weights['dependencies'], 0.1)
    
    def test_strategy_weights_fastest(self):
        weights = get_weights_for_strategy('fastest')
        self.assertEqual(weights['effort'], 0.5)
        self.assertEqual(weights['urgency'], 0.2)
    
    def test_strategy_weights_impact(self):
        weights = get_weights_for_strategy('impact')
        self.assertEqual(weights['importance'], 0.6)
    
    def test_strategy_weights_deadline(self):
        weights = get_weights_for_strategy('deadline')
        self.assertEqual(weights['urgency'], 0.7)
    
    def test_strategy_weights_default(self):
        weights = get_weights_for_strategy('invalid-strategy')
        self.assertEqual(weights['urgency'], 0.4)
    
    def test_date_string_parsing(self):
        date_str = '2025-12-01'
        score = self.scorer.calculate_urgency_score(date_str)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
