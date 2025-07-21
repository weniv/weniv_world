from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class StoryCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name="카테고리명")
    description = models.TextField(blank=True, verbose_name="설명")
    order = models.PositiveIntegerField(default=0, verbose_name="정렬순서")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        verbose_name = "스토리 카테고리"
        verbose_name_plural = "스토리 카테고리"
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Story(models.Model):
    DIFFICULTY_CHOICES = [
        (1, '입문'),
        (2, '기초'),
        (3, '중급'),
        (4, '고급'),
        (5, '전문가'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="스토리 내용")
    objectives = models.TextField(verbose_name="학습 목표")
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="난이도"
    )
    category = models.ForeignKey(
        StoryCategory, 
        on_delete=models.CASCADE,
        verbose_name="카테고리"
    )
    order = models.PositiveIntegerField(verbose_name="순서")
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    # 게임 월드 설정
    initial_world_data = models.JSONField(
        default=dict, 
        verbose_name="초기 월드 데이터",
        help_text="JSON 형태의 초기 게임 월드 설정"
    )
    solution_code = models.TextField(
        blank=True, 
        verbose_name="솔루션 코드",
        help_text="문제 해결을 위한 예시 코드"
    )
    
    # 이미지 및 미디어
    image_url = models.URLField(
        blank=True,
        verbose_name="스토리 이미지 URL"
    )
    
    class Meta:
        verbose_name = "스토리"
        verbose_name_plural = "스토리 관리"
        ordering = ['category__order', 'order']
        unique_together = ['category', 'order']
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['is_active']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.order}. {self.title}"
    
    def get_completion_rate(self):
        """완료율 계산"""
        from apps.progress.models import UserProgress
        total = UserProgress.objects.filter(story=self).count()
        if total == 0:
            return 0
        completed = UserProgress.objects.filter(
            story=self, completed=True
        ).count()
        return round((completed / total * 100), 1)
    
    def get_average_score(self):
        """평균 점수 계산"""
        from apps.progress.models import UserProgress
        from django.db.models import Avg
        result = UserProgress.objects.filter(
            story=self, completed=True
        ).aggregate(avg_score=Avg('score'))
        return round(result['avg_score'] or 0, 1)
    
    def get_average_attempts(self):
        """평균 시도 횟수 계산"""
        from apps.progress.models import UserProgress
        from django.db.models import Avg
        result = UserProgress.objects.filter(
            story=self
        ).aggregate(avg_attempts=Avg('attempts'))
        return round(result['avg_attempts'] or 0, 1)
    
    def get_next_story(self):
        """다음 스토리 반환"""
        return Story.objects.filter(
            category=self.category,
            order__gt=self.order,
            is_active=True
        ).first()
    
    def get_previous_story(self):
        """이전 스토리 반환"""
        return Story.objects.filter(
            category=self.category,
            order__lt=self.order,
            is_active=True
        ).last()
