// 섹션 크기 resize
const resizers = document.querySelectorAll('.resizer');

const resizable = (resizer) => {
    const direction = resizer.getAttribute('data-direction') || 'horizontal';
    const prevSibling = resizer.previousElementSibling;
    const nextSibling = resizer.nextElementSibling;

    let x = 0;
    let y = 0;
    let prevSiblingHeight = 0;
    let prevSiblingWidth = 0;

    const mouseDownHandler = (e) => {
        console.log(e);
        x = e.clientX;
        y = e.clientY;

        const rect = prevSibling.getBoundingClientRect();

        prevSiblingHeight = rect.height;
        prevSiblingWidth = rect.width;

        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
    };

    const mouseMoveHandler = (e) => {
        const dx = e.clientX - x;
        const dy = e.clientY - y;

        switch (direction) {
            case 'vertical':
                const height =
                    ((prevSiblingHeight + dy) * 100) /
                    resizer.parentNode.getBoundingClientRect().height;
                prevSibling.style.height = `${height}%`;
                break;
            case 'horizontal':
            default:
                const width =
                    ((prevSiblingWidth + dx) * 100) /
                    resizer.parentNode.getBoundingClientRect().width;
                prevSibling.style.width = `${width}%`;
                break;
        }

        const cursor = direction === 'horizontal' ? 'col-resize' : 'row-resize';
        resizer.style.cursor = cursor;
        document.body.style.cursor = cursor;

        prevSibling.style.userSelect = 'none';
        prevSibling.style.pointerEvents = 'none';

        nextSibling.style.userSelect = 'none';
        nextSibling.style.pointerEvents = 'none';
    };

    const mouseUpHandler = () => {
        resizer.style.removeProperty('cursor');
        document.body.style.removeProperty('cursor');

        prevSibling.style.removeProperty('user-select');
        prevSibling.style.removeProperty('pointer-events');

        nextSibling.style.removeProperty('user-select');
        nextSibling.style.removeProperty('pointer-events');

        document.removeEventListener('mousemove', mouseMoveHandler);
        document.removeEventListener('mouseup', mouseUpHandler);
    };

    resizer.addEventListener('mousedown', mouseDownHandler);
};

resizers.forEach((resizer) => {
    resizable(resizer);
});
