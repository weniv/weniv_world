from django.db import models
from django.utils import timezone

class GameSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True, verbose_name="세션 ID")
    story = models.ForeignKey(
        'story.Story', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="스토리"
    )
    world_data = models.JSONField(default=dict, verbose_name="월드 상태")
    character_data = models.JSONField(default=dict, verbose_name="캐릭터 상태")
    submitted_code = models.TextField(blank=True, verbose_name="제출 코드")
    is_completed = models.BooleanField(default=False, verbose_name="완료 여부")
    last_action_time = models.DateTimeField(default=timezone.now, verbose_name="마지막 액션 시간")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    # 게임 진행 관련
    score = models.IntegerField(default=0, verbose_name="점수")
    attempts = models.PositiveIntegerField(default=0, verbose_name="시도 횟수")
    hints_used = models.PositiveIntegerField(default=0, verbose_name="힌트 사용 횟수")
    
    class Meta:
        verbose_name = "게임 세션"
        verbose_name_plural = "게임 세션 관리"
        ordering = ['-updated_at']
    
    def __str__(self):
        story_title = self.story.title if self.story else "자유 모드"
        return f"{self.session_id} - {story_title}"
    
    def get_session_duration(self):
        """세션 지속 시간 계산"""
        if self.is_completed:
            return self.updated_at - self.created_at
        else:
            return timezone.now() - self.created_at
    
    def increment_attempts(self):
        """시도 횟수 증가"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
    
    def add_score(self, points):
        """점수 추가"""
        self.score += points
        self.save(update_fields=['score'])

class GameAsset(models.Model):
    ASSET_TYPES = [
        ('character', '캐릭터'),
        ('item', '아이템'),
        ('mob', '몹'),
        ('wall', '벽'),
        ('background', '배경'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="에셋명")
    asset_type = models.CharField(
        max_length=20, 
        choices=ASSET_TYPES,
        verbose_name="에셋 타입"
    )
    image_url = models.URLField(verbose_name="이미지 URL")
    properties = models.JSONField(default=dict, verbose_name="속성")
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        verbose_name = "게임 에셋"
        verbose_name_plural = "게임 에셋 관리"
        ordering = ['asset_type', 'name']
    
    def __str__(self):
        return f"{self.get_asset_type_display()} - {self.name}"

class GameAction(models.Model):
    ACTION_TYPES = [
        ('move', '이동'),
        ('turn_left', '왼쪽 회전'),
        ('pick', '아이템 줍기'),
        ('put', '아이템 놓기'),
        ('attack', '공격'),
        ('eat', '아이템 먹기'),
        ('say', '말하기'),
        ('open_door', '문 열기'),
    ]
    
    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="게임 세션"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="액션 타입"
    )
    action_data = models.JSONField(default=dict, verbose_name="액션 데이터")
    character_state_before = models.JSONField(default=dict, verbose_name="액션 전 캐릭터 상태")
    character_state_after = models.JSONField(default=dict, verbose_name="액션 후 캐릭터 상태")
    world_state_snapshot = models.JSONField(default=dict, verbose_name="월드 상태 스냅샷")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="실행 시간")
    execution_time_ms = models.PositiveIntegerField(default=0, verbose_name="실행 시간(ms)")
    
    class Meta:
        verbose_name = "게임 액션"
        verbose_name_plural = "게임 액션 로그"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.session.session_id} - {self.get_action_type_display()}"
