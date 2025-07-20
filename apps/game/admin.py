from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import GameSession, GameAsset, GameAction

class GameActionInline(admin.TabularInline):
    model = GameAction
    extra = 0
    readonly_fields = ['action_type', 'timestamp', 'execution_time_ms']
    fields = ['action_type', 'action_data', 'timestamp', 'execution_time_ms']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id', 'story', 'is_completed', 'score', 'attempts', 
        'duration_display', 'last_action_time'
    ]
    list_filter = ['is_completed', 'story__category', 'story__difficulty', 'created_at']
    search_fields = ['session_id', 'story__title']
    readonly_fields = ['created_at', 'updated_at', 'duration_display']
    
    fieldsets = (
        ('세션 정보', {
            'fields': ('session_id', 'story', 'is_completed')
        }),
        ('게임 진행', {
            'fields': ('score', 'attempts', 'hints_used', 'last_action_time')
        }),
        ('게임 데이터', {
            'fields': ('world_data', 'character_data', 'submitted_code'),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [GameActionInline]
    
    def duration_display(self, obj):
        duration = obj.get_session_duration()
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}시간 {minutes}분 {seconds}초"
        elif minutes > 0:
            return f"{minutes}분 {seconds}초"
        else:
            return f"{seconds}초"
    duration_display.short_description = "세션 지속 시간"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('story')

@admin.register(GameAsset)
class GameAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'image_preview', 'is_active', 'created_at']
    list_filter = ['asset_type', 'is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'asset_type', 'is_active')
        }),
        ('에셋 데이터', {
            'fields': ('image_url', 'properties')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;">',
                obj.image_url
            )
        return "-"
    image_preview.short_description = "미리보기"

@admin.register(GameAction)
class GameActionAdmin(admin.ModelAdmin):
    list_display = [
        'session', 'action_type', 'timestamp', 'execution_time_ms'
    ]
    list_filter = ['action_type', 'timestamp', 'session__story']
    search_fields = ['session__session_id', 'action_type']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('액션 정보', {
            'fields': ('session', 'action_type', 'timestamp', 'execution_time_ms')
        }),
        ('액션 데이터', {
            'fields': ('action_data',),
            'classes': ('collapse',)
        }),
        ('상태 스냅샷', {
            'fields': ('character_state_before', 'character_state_after', 'world_state_snapshot'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # 액션 로그는 시스템에서 자동 생성
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'session__story')
