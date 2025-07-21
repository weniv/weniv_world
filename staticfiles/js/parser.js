// 코드가 가독성과 재사용성이 떨어져 리뉴얼이 필요함
// https://codepen.io/kvendrik/pen/bGKeEE 코드로 리뉴얼할 예정

const parser = (markdown) => {
    const normalize = (markdown) => {
        return markdown
            .replace(/\r\n?/g, '\n')
            .replace(/\n{2,}/g, '\n\n')
            .split('\n');
    };

    const parse = (token, { regex, tagName, replace }) => {
        return token.replace(regex, replace ?? `<${tagName}>$1</${tagName}>`);
    };

    const codeBlockStart = {
        regex: /^\s*`{3}(.+)/,
        replace: '<pre class="md-pre"><code>$1',
    };

    const codeBlockEnd = {
        regex: /(.*)`{3}\s*$/,
        replace: '$1</code></pre>',
    };

    const unorderedListItem = {
        regex: /^\s*-\s(.+)/,
        replace: '<li class="md-ul-li">$1',
    };

    const orderedListItem = {
        regex: /^\s*(\d+\.\s)(.+)/,
        replace: '<li class="md-ol-li">$2',
        // 정규표현식
    };

    const tableRow = {
        regex: /^\|(.+)\|$/,
        replace: (_, group) => {
            const heads = group
                .split('|')
                .map((text) => `<td>${text.trim()}</td>`)
                .join('');
            return `<tr>${heads}</tr>`;
        },
    };

    const tableDivision = {
        regex: /^\|(([-|]|\s)+)\|$/,
        replace: '',
    };

    const blockquote = {
        regex: /^\s*(?:"|>|&#62;)\s(.+)/,
        replace: '<blockquote class="md-blockquote">$1</blockquote>',
    };

    const heading = {
        regex: /^\s*(#+)\s(.+)/,
        replace: (_, mark, group) => {
            const tagName = `h${mark.length + 1}`;

            if (mark.length == 1) {
                return `<${tagName} class="md-tit1" id="${group.replace(
                    /(\*{2})|`/g,
                    '',
                )}">${group}</${tagName}>`;
            } else if (mark.length == 2) {
                return `<${tagName} class="md-tit2" id="${group.replace(
                    /(\*{2})|`/g,
                    '',
                )}">${group}</${tagName}>`;
            } else if (mark.length == 3) {
                return `<${tagName} class="md-tit3" id="${group.replace(
                    /(\*{2})|`/g,
                    '',
                )}">${group}</${tagName}>`;
            }
            return `<${tagName} class="md-tit4" id="${group.replace(
                /(\*{2})|`/g,
                '',
            )}">${group}</${tagName}>`;
        },
    };

    const figure = {
        regex: /^\s*!\[(.*)\]\((.+)\)/,
        replace: (_, g1, g2) => {
            const width = g2.match(/_{2}(\d+)\..+$/)?.[1];
            return `<figure class="md-figure"><img class="md-img" loading="lazy" src="./assets/data/story/img/${g2}" ${
                width ? ` style="width: ${width}px;"` : ''
            } alt="">${g1 ? `<figcaption>${g1}</figcaption>` : ''}</figure>`;
        },
    };

    const lineBreak = {
        regex: /^<br\s*\/>$/,
        replace: '<br />',
    };

    const hrline = {
        regex: /---/,
        replace: '<hr class="md-hr" />',
    };

    const paragraph = {
        regex: /(?:^|\n)(.+)$/,
        tagName: 'p',
        replace: (matched, group) =>
            /\<(\/)?(h\d|ul|ol|li|blockquote|pre|img|code)/.test(matched)
                ? matched
                : '<p class="md-p">' + group + '</p>',
    };

    const link = {
        regex: /\[(.+)\]\((.+)\)/g,
        replace: '<a class="md-a" href="$2">$1</a>',
    };

    const strong = {
        regex: /\*{2}(([^*])+)\*{2}/g,
        tagName: 'strong',
    };

    const italic = {
        regex: /\*([^\*]+)\*/g,
        replace: '<i class="md-italic">$1</i>',
    };

    const code = {
        regex: /`([^`]+)`/g,
        tagName: 'code',
    };

    const del = {
        regex: /~{2}([^~]+)~{2}/g,
        replace: '<del class="md-del">$1</del>',
    };

    const listDepth = (token) => {
        const indentation = token.match(/^\s*(?=-|(\d+\.))/)[0].length;
        return indentation % 2 ? indentation - 1 : indentation;
    };

    const encodeEntity = (token) => {
        return token
            .replace(/<br\s*\/>/g, '&br /&')
            .replaceAll('<', '&#60;')
            .replaceAll('>', '&#62;')
            .replaceAll('&br /&', '<br />');
    };

    const encodeCodeEntity = (token) => {
        let keyword_syntex = [
            'def',
            'if',
            'else',
            'for',
            'while',
            'in',
            'return',
            'None',
        ];
        let keyword_builtinfunction = [
            'abs',
            'aiter',
            'all',
            'any',
            'anext',
            'ascii',
            'bin',
            'bool',
            'breakpoint',
            'bytearray',
            'bytes',
            'callable',
            'chr',
            'classmethod',
            'compile',
            'complex',
            'delattr',
            'dict',
            'dir',
            'divmod',
            'enumerate',
            'eval',
            'exec',
            'filter',
            'float',
            'format',
            'frozenset',
            'getattr',
            'globals',
            'hasattr',
            'hash',
            'help',
            'hex',
            'id',
            'input',
            'int',
            'isinstance',
            'issubclass',
            'iter',
            'len',
            'list',
            'locals',
            'map',
            'max',
            'memoryview',
            'min',
            'next',
            'object',
            'oct',
            'open',
            'ord',
            'pow',
            'print',
            'property',
            'range',
            'repr',
            'reversed',
            'round',
            'set',
            'setattr',
            'slice',
            'sorted',
            'staticmethod',
            'str',
            'sum',
            'super',
            'tuple',
            'type',
            'vars',
            'zip',
        ];

        keyword_syntex.forEach((key) => {
            const re = new RegExp(`(.*?)${key}[ ?(]+(.*?)`);
            token = token.replace(
                re,
                `$1<span class="code-syntex";>${key} </span>$2`,
            );
        });

        keyword_builtinfunction.forEach((key) => {
            const re = new RegExp(`(.*?) ${key}[ (]+(.*?)`);
            token = token.replace(
                re,
                `$1<span class="code-builtinfunction";> ${key}</span>($2`,
            );
        });

        const re = new RegExp(`(.*?)'(.*?)'(.*?)`, 'g');
        token = token.replace(re, `$1<span class="code-text";>'$2'</span>$3`);

        return token;
    };

    const blockRules = [
        codeBlockStart,
        unorderedListItem,
        orderedListItem,
        tableDivision,
        tableRow,
        heading,
        figure,
        lineBreak,
        hrline,
        blockquote,
    ];

    const inlineRules = [link, strong, code, italic, del];

    const parseMarkdown = (markdown) => {
        const tokens = normalize(markdown);
        let isEditor = false;
        let codeBlockStartIndex = -1;
        let tableStartIndex = -1;
        let curListDepth = -1;
        const listStack = [];
        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];
            // 코드 블럭이 아닐 때
            if (codeBlockStartIndex === -1) {
                const rule =
                    blockRules.find(({ regex }) => regex.test(token)) ??
                    paragraph;
                tokens[i] = parse(encodeEntity(token), rule);
                switch (rule) {
                    case codeBlockStart:
                        codeBlockStartIndex = i;
                        const codeType = tokens[i].match(/<code>(.+)$/)?.[1];
                        if (codeType === 'editor') {
                            isEditor = true;
                            tokens[i] = '';
                        } else {
                            tokens[i] = tokens[i].replace(codeType, '');
                        }
                        break;

                    case unorderedListItem:
                    case orderedListItem:
                        const tagName =
                            rule === unorderedListItem ? 'ul' : 'ol';
                        const depth = listDepth(token);
                        if (depth > curListDepth) {
                            tokens[i] =
                                `<${tagName} class='md-list'>` + tokens[i];
                            listStack.push(`</${tagName}>`);
                        } else if (depth < curListDepth) {
                            let depthDiff = (curListDepth - depth) / 2;
                            while (depthDiff) {
                                const tag = listStack.pop();
                                tokens[i - 1] += tag;
                                if (tag === `</${tagName}>`) {
                                    depthDiff--;
                                }
                            }
                            tokens[i - 1] += listStack.pop();
                        } else {
                            tokens[i - 1] += listStack.pop();
                        }
                        curListDepth = depth;
                        listStack.push('</li>');
                        break;

                    case tableRow:
                        if (tableStartIndex === -1) {
                            tableStartIndex = i;
                            tokens[i] =
                                '<table class="md-table">' +
                                tokens[i].replace(/(\<\/?)td>/g, '$1th>');
                        }
                        break;

                    default:
                        if (token.trim() === '') {
                            if (listStack.length) {
                                while (listStack.length) {
                                    tokens[i - 1] += listStack.pop();
                                }
                                curListDepth = -1;
                            }

                            if (tableStartIndex >= 0) {
                                tokens[i - 1] += '</table>';
                                tableStartIndex = -1;
                            }

                            isEditor = false;
                        }
                }
                // 코드 블럭일 때
            } else {
                if (token.trim() === '') {
                    tokens[i] = '\n\n';
                }
                if (!isEditor) {
                    tokens[i] = encodeCodeEntity(token);
                }
                if (codeBlockEnd.regex.test(token)) {
                    tokens[i] = parse(token, codeBlockEnd);
                    codeBlockStartIndex = -1;
                    isEditor = false;
                } else {
                    tokens[i] += '\n';
                }
            }
        }

        tokens.forEach((_, index) => {
            inlineRules.forEach((rule) => {
                if (rule.regex.test(tokens[index])) {
                    tokens[index] = parse(tokens[index], rule);
                }
            });
        });

        return tokens.filter(Boolean);
    };

    return parseMarkdown(markdown);
};

// export default parser;

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
        markdownData.forEach((data, index) => {
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

            if (localStorage.getItem(`${index + 1}_check`) === '정답') {
                li.classList.add('submit');
            }
            const submitButton = document.createElement('button');
            submitButton.setAttribute('class', 'btn-submit');
            submitButton.setAttribute('type', 'button');
            submitButton.innerText = '제출하기';

            titleSection.append(heading, submitButton, button);

            const contentSection = document.createElement('section');
            contentSection.setAttribute('class', 'story-contents');
            contentSection.innerHTML = data.content;

            contentSection.appendChild(submitButton.cloneNode(true));

            li.append(titleSection, contentSection);
            $storyList.appendChild(li);
        });
};

const render = async () => {
    const markdownData = await fetchMarkdown();
    renderContent(markdownData);
};

render();
