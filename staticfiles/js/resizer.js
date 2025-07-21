// 섹션 크기 resize
const resizers = document.querySelectorAll('.resizer');

const resizable = (resizer) => {
    const direction = resizer.getAttribute('data-direction') || 'horizontal';
    const target = resizer.getAttribute('data-target') || 'prev';
    const prevSibling = resizer.previousElementSibling;
    const nextSibling = resizer.nextElementSibling;
    const targetSibling =
        target == 'prev'
            ? resizer.previousElementSibling
            : resizer.nextElementSibling;

    let x = 0;
    let y = 0;
    let targetSiblingHeight = 0;
    let targetSiblingWidth = 0;

    const mouseDownHandler = (e) => {
        x = e.clientX;
        y = e.clientY;

        const rect = targetSibling.getBoundingClientRect();

        targetSiblingHeight = rect.height;
        targetSiblingWidth = rect.width;

        resizer.classList.add('active');
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
    };

    const mouseMoveHandler = (e) => {
        const dx = target == 'prev' ? e.clientX - x : x - e.clientX;
        const dy = target == 'prev' ? e.clientY - y : y - e.clientY;

        switch (direction) {
            case 'vertical':
                const height =
                    ((targetSiblingHeight + dy) * 100) /
                    resizer.parentNode.getBoundingClientRect().height;
                targetSibling.style.height = `${height}%`;
                break;
            case 'horizontal':
            default:
                const width =
                    ((targetSiblingWidth + dx) * 100) /
                    resizer.parentNode.getBoundingClientRect().width;
                targetSibling.style.width = `${width}%`;
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

        resizer.classList.remove('active');
        document.removeEventListener('mousemove', mouseMoveHandler);
        document.removeEventListener('mouseup', mouseUpHandler);
    };

    resizer.addEventListener('mousedown', mouseDownHandler);
};

resizers.forEach((resizer) => {
    resizable(resizer);
});
