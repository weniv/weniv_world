import { default as parser } from './parser.js';

const fetchMarkdown = async () => {
    const response = await fetch('./assets/data/story/story.json');
    const jsonData = await response.json();
    const mdArr = [];

    if (response.status == 200) {
        for (const item of jsonData) {
            const mdData = await fetch(item.url);
            if (mdData.status == 200) {
                const markdown = await mdData.text();

                if (markdown.length > 0) {
                    const parsedMarkdown = parser(markdown);
                    const infoObj = {
                        id: item.id,
                        title: item.title,
                        content: parsedMarkdown.join(''),
                    };

                    mdArr.push(infoObj);
                }
            }
        }
        return mdArr;
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
    const markdownData = await fetchMarkdown();
    renderContent(markdownData);
};

render();
