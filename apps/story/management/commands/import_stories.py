"""
기존 스토리 데이터를 Django 모델로 이전하는 관리 명령어
"""
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.story.models import Story, StoryCategory


class Command(BaseCommand):
    help = '기존 스토리 데이터를 Django 모델로 이전합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--story-json',
            type=str,
            default='static/data/story/story.json',
            help='스토리 JSON 파일 경로'
        )
        parser.add_argument(
            '--story-dir',
            type=str,
            default='static/data/story/',
            help='스토리 마크다운 파일 디렉토리 경로'
        )
        parser.add_argument(
            '--coordinate-py',
            type=str,
            default='static/py/coordinate.py',
            help='coordinate.py 파일 경로 (스토리 데이터 포함)'
        )

    def handle(self, *args, **options):
        story_json_path = options['story_json']
        story_dir_path = options['story_dir']
        coordinate_py_path = options['coordinate_py']

        self.stdout.write(
            self.style.SUCCESS('스토리 데이터 이전을 시작합니다...')
        )

        # 1. 기본 카테고리 생성
        default_category = self.create_default_category()

        # 2. story.json에서 기본 스토리 정보 로드
        story_list = self.load_story_json(story_json_path)

        # 3. coordinate.py에서 스토리별 게임 데이터 로드
        coordinate_data = self.load_coordinate_data(coordinate_py_path)

        # 4. 각 스토리의 마크다운 콘텐츠 로드 및 Django 모델 생성
        for story_info in story_list:
            self.create_story_model(
                story_info, 
                story_dir_path, 
                default_category,
                coordinate_data
            )

        self.stdout.write(
            self.style.SUCCESS(f'총 {len(story_list)}개의 스토리가 성공적으로 이전되었습니다.')
        )

    def create_default_category(self):
        """기본 스토리 카테고리 생성"""
        category, created = StoryCategory.objects.get_or_create(
            name="위니브 월드 기본 스토리",
            defaults={
                'description': "위니브 월드의 22개 기본 스토리들",
                'order': 1
            }
        )
        
        if created:
            self.stdout.write(f"기본 카테고리 생성: {category.name}")
        else:
            self.stdout.write(f"기본 카테고리 사용: {category.name}")
            
        return category

    def load_story_json(self, json_path):
        """story.json 파일 로드"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"story.json 로드 실패: {e}")
            )
            return []

    def load_coordinate_data(self, coordinate_path):
        """coordinate.py에서 story_data 추출"""
        coordinate_data = {}
        
        try:
            # coordinate.py 파일을 읽어서 story_data 부분 추출
            with open(coordinate_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # story_data 딕셔너리 추출 (간단한 파싱)
            import re
            story_data_match = re.search(r'story_data\s*=\s*({.*?})\s*}', content, re.DOTALL)
            
            if story_data_match:
                # 보안상 eval 대신 ast.literal_eval 사용하거나 수동 파싱
                # 여기서는 간단히 coordinate.py를 임포트
                import sys
                import importlib.util
                
                spec = importlib.util.spec_from_file_location("coordinate", coordinate_path)
                coordinate_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(coordinate_module)
                
                if hasattr(coordinate_module, 'story_data'):
                    coordinate_data = coordinate_module.story_data
                    self.stdout.write(f"coordinate.py에서 {len(coordinate_data)}개 스토리 데이터 로드됨")
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"coordinate.py 로드 실패: {e}")
            )
            
        return coordinate_data

    def create_story_model(self, story_info, story_dir, category, coordinate_data):
        """개별 스토리 Django 모델 생성"""
        story_id = story_info['id']
        title = story_info['title']
        
        # 마크다운 파일 읽기
        md_filename = f"story{story_id}.md"
        md_path = os.path.join(story_dir, md_filename)
        
        content = ""
        if os.path.exists(md_path):
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"스토리 {story_id} 마크다운 로드 실패: {e}")
                )

        # coordinate.py에서 해당 스토리의 게임 데이터 가져오기
        story_coordinate_data = coordinate_data.get(story_id, {})
        
        # initial_world_data 구성 (tuple keys를 string으로 변환)
        wall_data = story_coordinate_data.get('wall', {})
        item_data = story_coordinate_data.get('item', {})
        
        # tuple key를 string으로 변환
        wall_data_str = {str(k): v for k, v in wall_data.items()}
        item_data_str = {str(k): v for k, v in item_data.items()}
        
        initial_world_data = {
            'map_width': story_coordinate_data.get('map_width', 5),
            'map_height': story_coordinate_data.get('map_height', 5),
            'wall_data': wall_data_str,
            'item_data': item_data_str,
            'mob_data': story_coordinate_data.get('mob_data', []),
            'basic_code': story_coordinate_data.get('basic_code', '')
        }

        # 난이도 추정 (평가 기준 개수로)
        evaluation = story_info.get('evaluation', [])
        difficulty = min(len(evaluation) + 1, 5)  # 1-5 범위

        # 학습 목표 생성
        objectives = f"이 스토리에서는 {', '.join(evaluation)}에 대해 학습합니다." if evaluation else "Python 기초 학습"

        # Story 모델 생성 또는 업데이트
        story, created = Story.objects.update_or_create(
            order=story_id,  # 기존 ID를 order로 사용
            defaults={
                'title': title,
                'content': content,
                'objectives': objectives,
                'difficulty': difficulty,
                'category': category,
                'initial_world_data': initial_world_data,
                'is_active': True
            }
        )

        action = "생성됨" if created else "업데이트됨"
        self.stdout.write(f"스토리 {story_id}: {title} - {action}")

        return story