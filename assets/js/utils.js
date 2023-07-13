const colorset = {
  white: "0xffffff",
  baseGround: "0x89b14c",
  lightGround: "0xa5c177",
  darkGround: "0x4f9036",
  water: "0x7ccad5",
  sky: "0xa8f4ff",
};

function colorvar(color) {
  return parseInt(colorset[color]);
}

export { colorset, colorvar };
