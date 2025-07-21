// import { default as parser } from './parser.js';

const fetchStories = async () => {
    try {
        // Django에서 미리 렌더링된 스토리 데이터가 있으면 그것을 사용
        if (typeof window.STORY_DATA !== 'undefined' && window.STORY_DATA) {
            return JSON.parse(window.STORY_DATA);
        }
        
        // 없다면 API에서 가져오기
        const response = await fetch('/api/stories/');
        const data = await response.json();
        
        if (response.status === 200 && data.success) {
            return data.stories.map(story => ({
                id: story.id,
                title: story.title,
                content: parser(story.content).join(''),
                objectives: story.objectives,
                difficulty: story.difficulty,
                order: story.order,
                category: story.category,
                initial_world_data: story.initial_world_data
            }));
        }
        
        console.error('Failed to fetch stories:', data);
        return [];
    } catch (error) {
        console.error('Error fetching stories:', error);
        return [];
    }
};

const renderContent = (markdownData) => {
    const $storyList = document.querySelector('.story-list');

    markdownData &&
        markdownData.forEach((data) => {
            const li = document.createElement('li');
            const titleSection = document.createElement('section');
            titleSection.setAttribute('class', 'story-title');

            const heading = document.createElement('h3');
            heading.setAttribute('class', 'sl-ellipsis');
            heading.innerHTML = `<span>${data.id}편</span>${data.title}`;

            const button = document.createElement('button');
            button.setAttribute('type', 'button');
            button.setAttribute('class', 'btn-toggle');
            button.innerHTML = `<span class="sr-only">스토리 여닫기</span>`;

            titleSection.append(heading, button);

            const contentSection = document.createElement('section');
            contentSection.setAttribute('class', 'story-contents');
            contentSection.innerHTML = data.content;

            li.append(titleSection, contentSection);
            $storyList.appendChild(li);
        });
};

const render = async () => {
    const storyData = await fetchStories();
    renderContent(storyData);
};

render();
