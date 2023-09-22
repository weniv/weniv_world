const colorset = {
    white: '0xffffff',
    baseGround: '0x89b14c',
    lightGround: '0xa5c177',
    darkGround: '0x4f9036',
    water: '0x7ccad5',
    sky: '0xa8f4ff',
};

function colorvar(color) {
    return parseInt(colorset[color]);
}
export { colorset, colorvar, dateFormat};

const dateFormat = ()=> {
    // yyyy-mm-dd-hh-mm-ss korean time
    const date = new Date();
    let format = '';
    format += date.getFullYear() + '-';
    format += (date.getMonth() + 1) + '-';
    format += date.getDate() + '-';
    format += date.getHours() + '-';
    format += date.getMinutes() + '-';
    format += date.getSeconds();
    return format;
};

