from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .scoring import TaskScorer, get_weights_for_strategy

@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and prioritize tasks based on multiple factors
    Accepts a list of tasks and returns them sorted by priority score
    """
    try:
        tasks = request.data
        
        # Validate input
        if not isinstance(tasks, list):
            return Response(
                {'error': 'Expected a list of tasks'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(tasks) == 0:
            return Response(
                {'error': 'No tasks provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate each task
        for i, task in enumerate(tasks):
            if not all(k in task for k in ['title', 'due_date', 'estimated_hours', 'importance']):
                return Response(
                    {'error': f'Task {i} missing required fields. Each task must have title, due_date, estimated_hours, and importance'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate importance range
            if not (1 <= task['importance'] <= 10):
                return Response(
                    {'error': f'Task "{task["title"]}" has invalid importance. Must be between 1-10'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate estimated hours
            if task['estimated_hours'] <= 0:
                return Response(
                    {'error': f'Task "{task["title"]}" has invalid estimated hours. Must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get strategy from query params
        strategy = request.GET.get('strategy', 'smart')
        weights = get_weights_for_strategy(strategy)
        
        # Calculate scores for all tasks
        scorer = TaskScorer(weights)
        scored_tasks = []
        
        for task in tasks:
            score = scorer.calculate_total_score(task, tasks)
            task_with_score = task.copy()
            task_with_score['priority_score'] = score
            task_with_score['strategy_used'] = strategy
            scored_tasks.append(task_with_score)
        
        # Sort by priority score (descending)
        sorted_tasks = sorted(scored_tasks, key=lambda x: x['priority_score'], reverse=True)
        
        return Response({
            'tasks': sorted_tasks,
            'strategy_used': strategy,
            'total_tasks': len(sorted_tasks)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def suggest_tasks(request):
    """
    Suggest top 3 tasks to work on today
    This is a simplified version that would typically work with stored tasks
    """
    try:
        # In a real application, this would fetch tasks from database
        # For this assignment, we'll return sample suggestions
        
        sample_suggestions = [
            {
                'title': 'Fix critical login bug',
                'reason': 'High importance (9/10) and blocking user access',
                'priority_score': 0.92,
                'due_date': '2025-11-25',
                'estimated_hours': 4,
                'importance': 9
            },
            {
                'title': 'Complete project documentation',
                'reason': 'Quick win - only 2 hours estimated and due tomorrow',
                'priority_score': 0.78,
                'due_date': '2025-11-26',
                'estimated_hours': 2,
                'importance': 7
            },
            {
                'title': 'Setup production monitoring',
                'reason': 'Blocks deployment of 3 other features',
                'priority_score': 0.71,
                'due_date': '2025-11-28',
                'estimated_hours': 6,
                'importance': 8
            }
        ]
        
        return Response({
            'suggestions': sample_suggestions,
            'message': 'Top 3 recommended tasks for today'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def api_info(request):
    """API information endpoint"""
    return Response({
        'name': 'Smart Task Analyzer API',
        'version': '1.0',
        'endpoints': {
            'POST /api/tasks/analyze/': 'Analyze and prioritize tasks',
            'GET /api/tasks/suggest/': 'Get task suggestions for today',
            'GET /api/info/': 'API information'
        },
        'strategies': ['smart', 'fastest', 'impact', 'deadline']
    })