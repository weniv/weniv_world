from django.shortcuts import render
from django.http import JsonResponse
import json

from apps.story.models import Story


def index(request):
    """메인 게임 페이지"""
    # 활성화된 스토리들을 카테고리와 순서에 따라 정렬
    stories = Story.objects.filter(is_active=True).select_related('category').order_by('category__order', 'order')
    
    # JavaScript에서 사용할 스토리 데이터 직렬화
    stories_json = []
    for story in stories:
        stories_json.append({
            'id': story.id,
            'title': story.title,
            'content': story.content,
            'objectives': story.objectives,
            'difficulty': story.difficulty,
            'order': story.order,
            'category': {
                'id': story.category.id,
                'name': story.category.name,
                'order': story.category.order
            } if story.category else None,
            'initial_world_data': story.initial_world_data,
        })

    context = {
        'stories': json.dumps(stories_json),  # JavaScript에서 사용할 JSON 데이터
        'story_categories': stories.values_list('category__name', flat=True).distinct()
    }
    
    return render(request, 'index.html', context)
