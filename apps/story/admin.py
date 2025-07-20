from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Story, StoryCategory

@admin.register(StoryCategory)
class StoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'order', 'story_count', 'created_at']
    list_editable = ['order']
    ordering = ['order']
    search_fields = ['name', 'description']
    
    def story_count(self, obj):
        count = obj.story_set.count()
        url = reverse('admin:story_story_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} 개</a>', url, count)
    story_count.short_description = "스토리 수"

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'title', 'category', 'difficulty', 
        'completion_rate_display', 'average_score_display', 'is_active', 'updated_at'
    ]
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'objectives']
    list_editable = ['difficulty', 'is_active']
    list_display_links = ['order', 'title']
    ordering = ['category__order', 'order']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'category', 'order', 'difficulty', 'is_active')
        }),
        ('콘텐츠', {
            'fields': ('content', 'objectives', 'image_url'),
            'classes': ('wide',)
        }),
        ('게임 설정', {
            'fields': ('initial_world_data', 'solution_code'),
            'classes': ('collapse',),
            'description': 'JSON 형태로 초기 게임 월드 데이터를 설정하세요.'
        }),
    )
    
    actions = ['duplicate_stories', 'activate_stories', 'deactivate_stories']
    
    def completion_rate_display(self, obj):
        rate = obj.get_completion_rate()
        color = 'green' if rate > 70 else 'orange' if rate > 40 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    completion_rate_display.short_description = "완료율"
    
    def average_score_display(self, obj):
        score = obj.get_average_score()
        color = 'green' if score > 80 else 'orange' if score > 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}점</span>',
            color, score
        )
    average_score_display.short_description = "평균 점수"
    
    def duplicate_stories(self, request, queryset):
        """선택된 스토리 복사"""
        for story in queryset:
            story.pk = None
            story.title += " (복사본)"
            story.order += 1000  # 임시 순서
            story.save()
        self.message_user(request, f"{queryset.count()}개 스토리가 복사되었습니다.")
    duplicate_stories.short_description = "선택된 스토리 복사"
    
    def activate_stories(self, request, queryset):
        """선택된 스토리 활성화"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated}개 스토리가 활성화되었습니다.")
    activate_stories.short_description = "선택된 스토리 활성화"
    
    def deactivate_stories(self, request, queryset):
        """선택된 스토리 비활성화"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated}개 스토리가 비활성화되었습니다.")
    deactivate_stories.short_description = "선택된 스토리 비활성화"
