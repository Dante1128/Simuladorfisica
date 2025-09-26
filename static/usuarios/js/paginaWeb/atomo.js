let scene, camera, renderer, atom;
let nucleus,
  electrons = [];
let orbits = [];
let particles = [];
let mouseX = 0,
  mouseY = 0;
let colorScheme = 0;
let speed = 1;
let exploded = false;
let time = 0;

const colorSchemes = [
  {
    nucleus: 0xff6b6b,
    electrons: [0x4ecdc4, 0x45b7d1, 0x96ceb4],
    glow: 0xff6b6b,
  },
  {
    nucleus: 0xff9f43,
    electrons: [0xff6b6b, 0xfeca57, 0x48dbfb],
    glow: 0xff9f43,
  },
  {
    nucleus: 0x9c88ff,
    electrons: [0xff9ff3, 0x54a0ff, 0x5f27cd],
    glow: 0x9c88ff,
  },
  {
    nucleus: 0x00d2d3,
    electrons: [0xff9ff3, 0xfffa65, 0xff6348],
    glow: 0x00d2d3,
  },
];

function init() {
  scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x000000, 50, 200);
  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.z = 30;
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x000000, 0);
  document.getElementById("container").appendChild(renderer.domElement);

  createAtom();
  createStarField();
  document.addEventListener("mousemove", onMouseMove);
  window.addEventListener("resize", onWindowResize);

  animate();
}

function createAtom() {
  atom = new THREE.Group();

  // Crear núcleo con efecto de brillo
  const nucleusGeometry = new THREE.SphereGeometry(2, 32, 32);
  const nucleusMaterial = new THREE.MeshBasicMaterial({
    color: colorSchemes[colorScheme].nucleus,
    transparent: true,
    opacity: 0.9,
  });
  nucleus = new THREE.Mesh(nucleusGeometry, nucleusMaterial);

  // Efecto de brillo para el núcleo
  const glowGeometry = new THREE.SphereGeometry(3, 32, 32);
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: colorSchemes[colorScheme].glow,
    transparent: true,
    opacity: 0.3,
  });
  const glow = new THREE.Mesh(glowGeometry, glowMaterial);
  nucleus.add(glow);

  atom.add(nucleus);

  // Crear órbitas y electrones
  for (let i = 0; i < 3; i++) {
    createOrbit(i);
  }

  scene.add(atom);
}

function createOrbit(index) {
  const radius = 8 + index * 4;
  const segments = 128;

  // Crear órbita visible
  const orbitGeometry = new THREE.RingGeometry(
    radius - 0.1,
    radius + 0.1,
    segments
  );
  const orbitMaterial = new THREE.MeshBasicMaterial({
    color: colorSchemes[colorScheme].electrons[index],
    transparent: true,
    opacity: 0.2,
    side: THREE.DoubleSide,
  });
  const orbit = new THREE.Mesh(orbitGeometry, orbitMaterial);

  // Rotar órbitas en diferentes ángulos
  orbit.rotation.x = Math.PI / 2 + (index * Math.PI) / 6;
  orbit.rotation.y = (index * Math.PI) / 4;

  orbits.push(orbit);
  atom.add(orbit);

  // Crear electrones
  for (let j = 0; j < 2 + index; j++) {
    const electronGeometry = new THREE.SphereGeometry(0.5, 16, 16);
    const electronMaterial = new THREE.MeshBasicMaterial({
      color: colorSchemes[colorScheme].electrons[index],
      transparent: true,
      opacity: 0.8,
    });
    const electron = new THREE.Mesh(electronGeometry, electronMaterial);

    // Crear trail de partículas para cada electrón
    const trail = createTrail(colorSchemes[colorScheme].electrons[index]);
    electron.add(trail);

    electrons.push({
      mesh: electron,
      orbit: index,
      angle: (j / (2 + index)) * Math.PI * 2,
      speed: 0.02 + index * 0.01,
      radius: radius,
      trail: trail,
      trailPositions: [],
    });

    atom.add(electron);
  }
}

function createTrail(color) {
  const trailGeometry = new THREE.BufferGeometry();
  const positions = new Float32Array(30 * 3); // 10 puntos
  trailGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(positions, 3)
  );

  const trailMaterial = new THREE.LineBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.6,
  });

  return new THREE.Line(trailGeometry, trailMaterial);
}

function createStarField() {
  const starsGeometry = new THREE.BufferGeometry();
  const starsCount = 1000;
  const positions = new Float32Array(starsCount * 3);

  for (let i = 0; i < starsCount * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 200;
    positions[i + 1] = (Math.random() - 0.5) * 200;
    positions[i + 2] = (Math.random() - 0.5) * 200;
  }

  starsGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(positions, 3)
  );

  const starsMaterial = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.5,
    transparent: true,
    opacity: 0.8,
  });

  const stars = new THREE.Points(starsGeometry, starsMaterial);
  scene.add(stars);
}

function updateElectrons() {
  electrons.forEach((electronData, index) => {
    if (!exploded) {
      // Movimiento orbital normal
      electronData.angle += electronData.speed * speed;

      const x = Math.cos(electronData.angle) * electronData.radius;
      const y = Math.sin(electronData.angle) * electronData.radius;
      const z = Math.sin(electronData.angle * 2) * 3;

      // Aplicar rotación de la órbita
      const orbitRotation = orbits[electronData.orbit].rotation;
      const rotatedPos = new THREE.Vector3(x, y, z);
      rotatedPos.applyEuler(orbitRotation);

      electronData.mesh.position.copy(rotatedPos);

      // Efecto de pulsación en los electrones
      const pulse = 1 + Math.sin(time * 6 + index) * 0.2;
      electronData.mesh.scale.setScalar(pulse);
    } else {
      // Movimiento explosivo
      electronData.mesh.position.x += (Math.random() - 0.5) * 0.5;
      electronData.mesh.position.y += (Math.random() - 0.5) * 0.5;
      electronData.mesh.position.z += (Math.random() - 0.5) * 0.5;
    }
  });
}

function updateTrail(electronData) {
  const positions = electronData.trail.geometry.attributes.position.array;

  // Agregar nueva posición
  electronData.trailPositions.unshift(electronData.mesh.position.clone());

  // Mantener solo las últimas 10 posiciones
  if (electronData.trailPositions.length > 10) {
    electronData.trailPositions.pop();
  }

  // Actualizar geometría del trail
  for (let i = 0; i < electronData.trailPositions.length && i < 10; i++) {
    const pos = electronData.trailPositions[i];
    positions[i * 3] = pos.x;
    positions[i * 3 + 1] = pos.y;
    positions[i * 3 + 2] = pos.z;
  }

  electronData.trail.geometry.attributes.position.needsUpdate = true;
}

function onMouseMove(event) {
  mouseX = (event.clientX - window.innerWidth / 2) * 0.001;
  mouseY = (event.clientY - window.innerHeight / 2) * 0.001;
}

function onWindowResize() {
  camera.aspect = 1; 
  camera.updateProjectionMatrix();
  renderer.setSize(500, 500);
}

function changeColors() {
  colorScheme = (colorScheme + 1) % colorSchemes.length;

  // Actualizar colores del núcleo
  nucleus.material.color.setHex(colorSchemes[colorScheme].nucleus);
  nucleus.children[0].material.color.setHex(colorSchemes[colorScheme].glow);

  // Actualizar colores de órbitas y electrones
  electrons.forEach((electronData) => {
    const newColor = colorSchemes[colorScheme].electrons[electronData.orbit];
    electronData.mesh.material.color.setHex(newColor);
    electronData.trail.material.color.setHex(newColor);
  });

  orbits.forEach((orbit, index) => {
    orbit.material.color.setHex(colorSchemes[colorScheme].electrons[index]);
  });
}

function changeSpeed() {
  speed = speed >= 3 ? 0.5 : speed + 0.5;
}

function explode() {
  exploded = !exploded;
  if (!exploded) {
    // Reset posiciones
    electrons.forEach((electronData) => {
      electronData.trailPositions = [];
    });
  }
}

function reset() {
  exploded = false;
  speed = 1;
  electrons.forEach((electronData) => {
    electronData.angle = Math.random() * Math.PI * 2;
    electronData.trailPositions = [];
  });
}

function animate() {
  requestAnimationFrame(animate);
  time += 0.01;

  // Rotación del átomo basada en el mouse
  if (atom) {
    atom.rotation.x += (mouseY - atom.rotation.x) * 0.1;
    atom.rotation.y += (mouseX - atom.rotation.y) * 0.1;

    // Agregar rotación automática
    atom.rotation.z += 0.005 * speed;
  }

  // Animación del núcleo
  if (nucleus) {
    nucleus.scale.setScalar(1 + Math.sin(time * 3) * 0.1);
    nucleus.rotation.x += 0.01 * speed;
    nucleus.rotation.y += 0.015 * speed;

    // Efecto de pulsación del brillo
    nucleus.children[0].scale.setScalar(1 + Math.sin(time * 5) * 0.3);
    nucleus.children[0].material.opacity = 0.3 + Math.sin(time * 4) * 0.2;
  }

  // Actualizar electrones
  updateElectrons();

  // Animación de órbitas
  orbits.forEach((orbit, index) => {
    orbit.rotation.z += (0.001 + index * 0.002) * speed;
    orbit.material.opacity = 0.2 + Math.sin(time * 2 + index) * 0.1;
  });

  // Efectos de cámara
  camera.position.z = 30 + Math.sin(time * 0.5) * 5;

  renderer.render(scene, camera);
}

// Inicializar cuando se carga la página
init();
