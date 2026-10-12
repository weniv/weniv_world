// data-src(raw 화면, 1680×1050 기준 좌표) + data-crop="x y w h" → 그 부분만 상자에 꽉 차게 보여 준다
for (const el of document.querySelectorAll('[data-src]')) {
    const [x, y, w, h] = (el.dataset.crop || '0 0 1680 1050').split(' ').map(Number);
    const scale = el.clientWidth / w;
    el.style.height = `${h * scale}px`;
    el.style.backgroundImage = `url(${el.dataset.src})`;
    el.style.backgroundSize = `${1680 * scale}px ${1050 * scale}px`;
    el.style.backgroundPosition = `${-x * scale}px ${-y * scale}px`;
}
