from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # 게임 API 엔드포인트
    path('game/', views.GameAPIView.as_view(), name='game_api'),
    path('execute-code/', views.execute_code, name='execute_code'),
    path('save-session/', views.save_session, name='save_session'),
    path('load-session/', views.load_session, name='load_session'),
    path('create-session/', views.create_session, name='create_session'),
    
    # 스토리 API 엔드포인트
    path('stories/', views.get_stories, name='get_stories'),
    path('stories/<int:story_id>/', views.get_story, name='get_story'),
]