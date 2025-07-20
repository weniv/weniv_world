from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Q
from .models import UserProgress, LearningAnalytics, LearningReport

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = [
        'session_id', 'story', 'completed', 'score', 
        'attempts', 'completion_time_display', 'efficiency_display', 'created_at'
    ]
    list_filter = ['completed', 'story__category', 'story__difficulty', 'created_at']
    search_fields = ['session_id', 'story__title']
    readonly_fields = ['created_at', 'completed_at', 'updated_at', 'efficiency_display']
    
    fieldsets = (
        ('진행 정보', {
            'fields': ('session_id', 'story', 'completed', 'completed_at')
        }),
        ('성과 정보', {
            'fields': ('score', 'attempts', 'hints_used', 'completion_time')
        }),
        ('학습 분석', {
            'fields': ('total_execution_time', 'error_count', 'successful_runs', 'efficiency_display'),
            'classes': ('collapse',)
        }),
        ('제출 코드', {
            'fields': ('submitted_code',),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'reset_progress']
    
    def completion_time_display(self, obj):
        if obj.completion_time:
            total_seconds = int(obj.completion_time.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}분 {seconds}초"
        return "-"
    completion_time_display.short_description = "완료 시간"
    
    def efficiency_display(self, obj):
        efficiency = obj.get_efficiency_score()
        if efficiency >= 80:
            color = 'green'
        elif efficiency >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, efficiency
        )
    efficiency_display.short_description = "효율성 점수"
    
    def mark_completed(self, request, queryset):
        """선택된 진행률을 완료로 표시"""
        updated = 0
        for progress in queryset:
            if not progress.completed:
                progress.mark_completed()
                updated += 1
        self.message_user(request, f"{updated}개 진행률이 완료로 표시되었습니다.")
    mark_completed.short_description = "완료로 표시"
    
    def reset_progress(self, request, queryset):
        """선택된 진행률 초기화"""
        updated = queryset.update(
            completed=False,
            score=0,
            attempts=0,
            completion_time=None,
            completed_at=None,
            error_count=0,
            successful_runs=0
        )
        self.message_user(request, f"{updated}개 진행률이 초기화되었습니다.")
    reset_progress.short_description = "진행률 초기화"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # 통계 데이터 추가
        stats = UserProgress.objects.aggregate(
            total_sessions=Count('id'),
            completed_sessions=Count('id', filter=Q(completed=True)),
            avg_score=Avg('score'),
            avg_attempts=Avg('attempts')
        )
        
        completion_rate = 0
        if stats['total_sessions'] > 0:
            completion_rate = (stats['completed_sessions'] / stats['total_sessions']) * 100
        
        extra_context['stats'] = {
            'total_sessions': stats['total_sessions'],
            'completion_rate': round(completion_rate, 1),
            'avg_score': round(stats['avg_score'] or 0, 1),
            'avg_attempts': round(stats['avg_attempts'] or 0, 1),
        }
        
        return super().changelist_view(request, extra_context)

@admin.register(LearningAnalytics)
class LearningAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'story', 'action_type', 'timestamp']
    list_filter = ['action_type', 'story__category', 'timestamp']
    search_fields = ['session_id', 'action_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('분석 정보', {
            'fields': ('session_id', 'story', 'action_type', 'timestamp')
        }),
        ('액션 데이터', {
            'fields': ('action_data',),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('user_agent', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # 분석 데이터는 시스템에서 자동 생성
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('story')

@admin.register(LearningReport)
class LearningReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_type', 'date_from', 'date_to', 'story', 
        'completion_rate_display', 'total_sessions', 'generated_at'
    ]
    list_filter = ['report_type', 'generated_at', 'story__category']
    search_fields = ['story__title']
    readonly_fields = ['generated_at', 'completion_rate_display']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('리포트 설정', {
            'fields': ('report_type', 'date_from', 'date_to', 'story')
        }),
        ('리포트 데이터', {
            'fields': (
                'total_sessions', 'completed_sessions', 'completion_rate_display',
                'average_completion_time', 'average_attempts', 'average_score'
            )
        }),
        ('상세 데이터', {
            'fields': ('report_data',),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['regenerate_reports']
    
    def completion_rate_display(self, obj):
        rate = obj.get_completion_rate()
        color = 'green' if rate > 70 else 'orange' if rate > 40 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    completion_rate_display.short_description = "완료율"
    
    def regenerate_reports(self, request, queryset):
        """선택된 리포트 재생성"""
        # 실제 구현에서는 리포트 생성 로직 호출
        updated = queryset.count()
        self.message_user(request, f"{updated}개 리포트가 재생성 대기열에 추가되었습니다.")
    regenerate_reports.short_description = "리포트 재생성"
