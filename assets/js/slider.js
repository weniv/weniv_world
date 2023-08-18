const sliders = document.querySelectorAll('.slider');

const setSliderTrack = (element) => {
    const value = element.value;
    const max = parseInt(element.max);
    const min = parseInt(element.min);
    const width = ((value - min) / (max - min)) * 100;
    const color = getComputedStyle(element).color;

    element.style.background = `linear-gradient(to right, ${color} 0%, ${color} ${width}%, #d9dbe0 ${width}%, #d9dbe0 100%)`;
};

sliders.forEach((slider) => {
    setSliderTrack(slider);

    slider.addEventListener('input', (e) => {
        if (e.target.tagName == 'INPUT') {
            setSliderTrack(e.target);
        }
    });
});
