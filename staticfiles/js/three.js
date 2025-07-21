import * as THREE from "three";
import { colorvar } from "./utils.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export default class App {
  constructor(size) {
    this._size = 3; // 기본값 5
    this._model = new THREE.Group();
    this._map = new THREE.Group(); //기본 맵 (n*n 크기)
    this._mapDeco = new THREE.Group(); //추가된 블럭
    this.paintColor = "lightGround";

    // 기본 구성 요소
    // 캔버스
    const $canvas = document.getElementById("result");
    this._canvas = $canvas;

    // 장면
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(colorvar("sky"));
    this._scene = scene;

    // 렌더러
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      canvas: $canvas,
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize($canvas.clientWidth, $canvas.clientHeight);
    this._renderer = renderer;

    // 카메라
    const camera = new THREE.PerspectiveCamera(
      50,
      $canvas.clientWidth / $canvas.clientHeight,
      0.1,
      100
    );
    camera.position.set(4, 5, 4);
    camera.lookAt(10, 0, 10);

    this._camera = camera;

    // 컨트롤: 화면 회전, 확대, 이동
    const controls = new OrbitControls(this._camera, this._canvas);
    controls.minDistance = 2;
    this._controls = controls;

    // 마우스 클릭 시 좌표값 조정
    const raycaster = new THREE.Raycaster();
    raycaster.params.Line.threshold = 0;
    this._raycaster = raycaster;

    this._setupLight();
    // .기본 구성 요소

    // 장면 생성
    // 지도
    this._setupMap();
    scene.add(this._mapDeco);

    // 모델(라이캣)
    this._importModel("/assets/model/licat.glb");
    scene.add(this._model);
    // .장면 생성

    // 화면 출력
    window.onresize = this._onResize.bind(this);
    this._onResize();

    window.addEventListener("mousemove", (e) => this._onMousemove(e));
    window.addEventListener("click", this._onClick.bind(this));
    window.addEventListener("contextmenu", this._addBlock.bind(this));

    requestAnimationFrame(this._onRender.bind(this));
    // .화면 출력
  }

  _setupLight() {
    const color = 0xffffff;
    const intensity = 1;

    const light = new THREE.DirectionalLight(color, intensity);
    light.position.set(-1, 2, 4);
    this._scene.add(light);

    // 기본 빛
    this._scene.add(new THREE.AmbientLight(0xffffff, 0.3));
  }

  _setupMap() {
    // 지도
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    for (let i = 0; i < this._size; i++) {
      for (let j = 0; j < this._size; j++) {
        const mesh = new THREE.Mesh(
          geometry,
          new THREE.MeshStandardMaterial({
            color: new THREE.Color(colorvar("baseGround")),
          })
        );
        mesh.position.set(i + 0.5, -0.5, j + 0.5);
        this._map.add(mesh);
      }
    }

    this._scene.add(this._map);

    // 격자
    const gridHelper = new THREE.GridHelper(
      this._size,
      this._size,
      0xffff00,
      0xffffff
    );
    gridHelper.position.y = 0.001; //겹침 방지
    gridHelper.position.set(this._size / 2, 0.001, this._size / 2);
    this._scene.add(gridHelper);

    // 축
    const axesHelper = new THREE.AxesHelper(this._size);
    axesHelper.position.y = 0.002; // 겹침 방지
    this._scene.add(axesHelper);
  }

  _onResize() {
    const width = this._canvas.clientWidth;
    const height = this._canvas.clientHeight;
    this._camera.aspect = width / height;
    this._camera.updateProjectionMatrix();

    this._renderer.setSize(width, height);
    this._renderer.render(this._scene, this._camera);
  }

  _onRender(time) {
    this._renderer.render(this._scene, this._camera);
    this._onUpdate(time);
    requestAnimationFrame(this._onRender.bind(this));
  }

  _onUpdate(time) {
    time *= 0.001;
  }

  _importModel(src) {
    const modelLoader = new GLTFLoader();
    modelLoader.load(src, (gltf) => {
      const model = gltf.scene;
      this._model.add(model);
      model.position.set(0.5, 0, 0.5);
      model.scale.set(0.2, 0.2, 0.2);
      this._scene.add(model);

      let dir = 0;
      window.addEventListener("keypress", (e) => {
        switch (e.key) {
          case "w":
          case "W":
          case "ㅈ":
            this.jump(model, dir);
            break;
          case "e":
          case "E":
          case "ㄷ":
            this.move(model, dir);
            break;
          case "r":
          case "R":
          case "ㄱ":
            dir = this.rotate(model, dir);
            break;
        }
      });
    });
  }

  move(model, dir) {
    const pos = model.position;
    let nx = pos.x,
      ny = pos.y,
      nz = pos.z;

    switch (dir) {
      case 0: // 하
        nz += 1;
        break;
      case 1: //우
        nx += 1;
        break;
      case 2: // 상
        nz -= 1;
        break;
      case 3: //좌
        nx -= 1;
        break;
    }
    if (this._movable(nx, ny, nz)) {
      // 앞으로 이동
      model.position.set(nx, ny, nz);
    } else if (this._movable(nx, ny - 1, nz)) {
      // 한 칸 아래로 이동
      model.position.set(nx, ny - 1, nz);
    } else {
      // 두 칸 부터는 이동 불가
      alert("이동할 수 없어요!");
    }
  }

  _movable(x, y, z) {
    if (x < 0 || x > this._size || z < 0 || z > this._size) {
      return false;
    }

    const maps = [...this._map.children, ...this._mapDeco.children];
    const array = maps.filter((el) => {
      return (
        !(el.type.includes("Helper") || el.type.includes("Light")) &&
        el.position.equals(new THREE.Vector3(x, y + 0.5, z))
      );
    });
    const floor = maps.filter((el) => {
      return (
        !(el.type.includes("Helper") || el.type.includes("Light")) &&
        el.position.equals(new THREE.Vector3(x, y - 0.5, z))
      );
    });
    if (!array.length && floor.length) {
      return true;
    }
    return false;
  }

  rotate(model, dir) {
    model.rotation.y += Math.PI / 2;
    return (dir + 1) % 4;
  }

  jump(model, dir) {
    const pos = model.position;
    let nx = pos.x,
      ny = pos.y + 1,
      nz = pos.z;

    switch (dir) {
      case 0: //
        nz += 1;
        break;
      case 1: //우
        nx += 1;
        break;
      case 2: // 하
        nz -= 1;
        break;
      case 3: //좌
        nx -= 1;
        break;
    }

    if (this._movable(nx, ny, nz)) {
      model.position.set(nx, ny, nz);
    } else {
      alert("점프할 수 없어요!");
    }
  }

  _setupModel(gltf) {
    const model = gltf.model;
  }

  _onMousemove(e) {
    const pointer = new THREE.Vector2();
    const rect = this._canvas.getBoundingClientRect();
    pointer.x = ((e.clientX - rect.left) / this._canvas.clientWidth) * 2 - 1;
    pointer.y = ((e.clientY - rect.top) / this._canvas.clientHeight) * -2 + 1;

    this._raycaster.setFromCamera(pointer, this._camera);
  }

  _onClick() {
    const intersects = this._raycaster.intersectObjects(this._map.children);
    if (intersects.length > 0) {
      intersects[0].object.material.color = new THREE.Color(
        colorvar(this.paintColor)
      );
    }
  }

  _addBlock() {
    const intersects = this._raycaster.intersectObjects([
      ...this._map.children,
      ...this._mapDeco.children,
    ]);
    if (intersects.length > 0) {
      const obj = intersects[0].object;
      console.log(intersects[0]);
      const pos = obj.position;
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(
        geometry,
        new THREE.MeshStandardMaterial({ color: obj.material.color })
      );

      const nx = pos.x,
        ny = pos.y + 1,
        nz = pos.z;

      if (this._addable(nx, ny, nz)) {
        mesh.position.set(nx, ny, nz);
        this._mapDeco.add(mesh);
      } else {
        alert("추가할 수 없어요!");
      }
    }
  }
  _addable(x, y, z) {
    const maps = [
      ...this._map.children,
      ...this._mapDeco.children,
      ...this._model.children,
    ];
    console.log(maps);
    const array = maps.filter((el) => {
      return (
        !(el.type.includes("Helper") || el.type.includes("Light")) &&
        (el.position.equals(new THREE.Vector3(x, y - 0.5, z)) ||
          el.position.equals(new THREE.Vector3(x, y, z)))
      );
    });

    if (!array.length) {
      return true;
    }
    return false;
  }
}
const myApp = new App();
