// World 아래의 Terminal (print 출력)

const MAX_LINES = 5000;

export class Terminal {
    constructor({ output, indexList, scroller, clearButton, downloadButton }) {
        this.output = output;
        this.indexList = indexList;
        this.scroller = scroller;
        this.count = 0;
        this.current = null;

        clearButton?.addEventListener('click', () => this.onClear?.());
        downloadButton?.addEventListener('click', () => this.download());
    }

    append(text, { error = false } = {}) {
        this.count += 1;
        const item = document.createElement('p');
        item.className = 'output-item current';
        item.textContent = text;
        if (error) item.dataset.error = 'true';

        const index = document.createElement('li');
        index.className = 'current';
        index.textContent = this.count;

        if (this.current) {
            this.current.item.classList.remove('current');
            this.current.index.classList.remove('current');
        }
        this.current = { item, index };
        this.output.appendChild(item);
        this.indexList.appendChild(index);

        while (this.output.childElementCount > MAX_LINES) {
            this.output.firstElementChild.remove();
            this.indexList.firstElementChild.remove();
        }
        this.scroller.scrollTop = this.scroller.scrollHeight;
    }

    clear() {
        this.output.replaceChildren();
        this.indexList.replaceChildren();
        this.count = 0;
        this.current = null;
    }

    download() {
        const lines = [...this.output.querySelectorAll('.output-item')].map(
            (p) => p.textContent,
        );
        const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'result.txt';
        link.click();
        setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    }
}
