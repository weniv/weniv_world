from django.db import models
from django.utils import timezone

class UserProgress(models.Model):
    session_id = models.CharField(max_length=100, verbose_name="사용자 세션 ID")
    story = models.ForeignKey(
        'story.Story',
        on_delete=models.CASCADE,
        verbose_name="스토리"
    )
    completed = models.BooleanField(default=False, verbose_name="완료 여부")
    score = models.IntegerField(default=0, verbose_name="점수")
    attempts = models.PositiveIntegerField(default=0, verbose_name="시도 횟수")
    completion_time = models.DurationField(null=True, blank=True, verbose_name="완료 시간")
    submitted_code = models.TextField(blank=True, verbose_name="제출 코드")
    hints_used = models.PositiveIntegerField(default=0, verbose_name="사용한 힌트 수")
    
    # 학습 분석 데이터
    total_execution_time = models.FloatField(default=0.0, verbose_name="총 실행 시간(초)")
    error_count = models.PositiveIntegerField(default=0, verbose_name="오류 발생 횟수")
    successful_runs = models.PositiveIntegerField(default=0, verbose_name="성공한 실행 횟수")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="시작일")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="완료일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최종 수정일")
    
    class Meta:
        verbose_name = "학습 진행률"
        verbose_name_plural = "학습 진행률 관리"
        unique_together = ['session_id', 'story']
        ordering = ['-updated_at']
    
    def __str__(self):
        status = "완료" if self.completed else "진행중"
        return f"{self.session_id} - {self.story.title} ({status})"
    
    def mark_completed(self):
        """완료 표시"""
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.completion_time = self.completed_at - self.created_at
            self.save(update_fields=['completed', 'completed_at', 'completion_time'])
    
    def add_attempt(self):
        """시도 횟수 증가"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
    
    def add_error(self):
        """오류 횟수 증가"""
        self.error_count += 1
        self.save(update_fields=['error_count'])
    
    def add_successful_run(self):
        """성공한 실행 횟수 증가"""
        self.successful_runs += 1
        self.save(update_fields=['successful_runs'])
    
    def get_completion_percentage(self):
        """완료율 계산 (0-100)"""
        return 100 if self.completed else 0
    
    def get_efficiency_score(self):
        """효율성 점수 계산"""
        if self.attempts == 0:
            return 0
        return max(0, 100 - (self.attempts - 1) * 10)  # 시도 횟수가 많을수록 점수 감소

class LearningAnalytics(models.Model):
    session_id = models.CharField(max_length=100, verbose_name="사용자 세션 ID")
    story = models.ForeignKey(
        'story.Story',
        on_delete=models.CASCADE,
        verbose_name="스토리"
    )
    action_type = models.CharField(max_length=50, verbose_name="액션 타입")
    action_data = models.JSONField(default=dict, verbose_name="액션 데이터")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="시간")
    
    # 분석 메타데이터
    user_agent = models.TextField(blank=True, verbose_name="사용자 에이전트")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP 주소")
    
    class Meta:
        verbose_name = "학습 분석"
        verbose_name_plural = "학습 분석 데이터"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session_id', 'story']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.session_id} - {self.action_type} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

class LearningReport(models.Model):
    REPORT_TYPES = [
        ('daily', '일일 리포트'),
        ('weekly', '주간 리포트'), 
        ('monthly', '월간 리포트'),
        ('story', '스토리별 리포트'),
    ]
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        verbose_name="리포트 타입"
    )
    date_from = models.DateField(verbose_name="시작 날짜")
    date_to = models.DateField(verbose_name="종료 날짜")
    story = models.ForeignKey(
        'story.Story',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="대상 스토리"
    )
    
    # 리포트 데이터
    total_sessions = models.PositiveIntegerField(default=0, verbose_name="총 세션 수")
    completed_sessions = models.PositiveIntegerField(default=0, verbose_name="완료된 세션 수")
    average_completion_time = models.DurationField(null=True, blank=True, verbose_name="평균 완료 시간")
    average_attempts = models.FloatField(default=0.0, verbose_name="평균 시도 횟수")
    average_score = models.FloatField(default=0.0, verbose_name="평균 점수")
    
    # 메타데이터
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    report_data = models.JSONField(default=dict, verbose_name="상세 리포트 데이터")
    
    class Meta:
        verbose_name = "학습 리포트"
        verbose_name_plural = "학습 리포트"
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} ({self.date_from} ~ {self.date_to})"
    
    def get_completion_rate(self):
        """완료율 계산"""
        if self.total_sessions == 0:
            return 0
        return round((self.completed_sessions / self.total_sessions) * 100, 1)
