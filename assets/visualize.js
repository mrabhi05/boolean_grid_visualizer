import { OrbitControls } from './OrbitControls.js';
import { BoxBufferGeometry, WebGLRenderer, PerspectiveCamera, Scene, Color, DoubleSide, PointLight, 
    Group, LineBasicMaterial, MeshPhongMaterial, LineSegments, Mesh } from "./three.module.js";
let scene;
let camera;
let renderer;
let group;
let grid_data;
let path_list;
// let stone_cold =[];
function animate() {
    requestAnimationFrame( animate );
    renderer.render( scene, camera );
}
function getGridData() {
    const urlParams = new URLSearchParams(window.location.search);
    let geom = urlParams.get('geom');
    if (geom == null) geom = 'geometry'
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange=function() {
        if (this.readyState == 4 && this.status == 200) {
            grid_data = JSON.parse(this.responseText);
            // console.log(grid_data)
            render();
        }
    };
    xhttp.open("GET", geom + "_grid_bool.json?t=" + Math.random(), true);
    xhttp.send();
}
function addGridToScene() {
  
    let meshMaterial = new MeshPhongMaterial({ color: 0x156289, emissive: 0x072534, side: DoubleSide, flatShading: true });
    let meshMaterial2 = new MeshPhongMaterial({ color: 0x00ff00, emissive: 0x072534, side: DoubleSide, flatShading: true });
    let meshMaterial3 = new MeshPhongMaterial({ color: 0x50ef9, emissive: 0x072534, side: DoubleSide, flatShading: true });
    group = new Group();
    let len_x = grid_data.length
    let len_y = grid_data[0].length
    let len_z = grid_data[0][0].length
    console.log({len_x, len_y, len_z})
    for (let i = 0; i < len_x; i++) {
        for (let j = 0; j < len_y; j++) {
            for (let k = 0; k < len_z; k++) {
                let geometry = new BoxBufferGeometry();
                geometry.translate(i - len_x/2, j - len_y/2, k - len_z/2);
                if (grid_data[i][j][k]) {
                    group.add(new Mesh(geometry, meshMaterial));    
                }
                if (grid_data[i][j][k] == 3){
                    group.add(new Mesh(geometry, meshMaterial2));
                }
                if (grid_data[i][j][k] == 4){
                    group.add(new Mesh(geometry, meshMaterial3));
                }
            }
        }
    }
    scene.add(group);
}
// function changeOrigin(path_list){
//     let Z_slicing = 11;
//     for(let i=0; i<path_list.length-1; i){
//         x = i[0]-20.25
//         y = i[1]-22.5
//         z = i[2]-(Z_slicing)/2;
//         stone_cold.push([x,y,z])
//     }
//}
function render() {
    scene = new Scene();
    scene.background = new Color(0x444444);
    camera = new PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
    renderer = new WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );
    camera.position.z = grid_data[0][0].length*3;
    let orbit = new OrbitControls(camera, renderer.domElement);
    // orbit.enableZoom = false;
    let lights = [];
    lights[0] = new PointLight(0xffffff, 1, 0);
    lights[1] = new PointLight(0xffffff, 1, 0);
    lights[2] = new PointLight(0xffffff, 1, 0);
    lights[0].position.set(0, 200, 0);
    lights[1].position.set(100, 200, 100);
    lights[2].position.set(- 100, - 200, - 100);
    scene.add(lights[0]);
    scene.add(lights[1]);
    scene.add(lights[2]);
    addGridToScene();
    animate();

    // To shift the orgin to the grid corner.
    let x_org = (152/2);
    let y_org = (57/2);
    let z_org = (5/2);
    path_list=[
                [2-x_org, 55-y_org, 1-z_org],
                [38-x_org, 55-y_org, 3-z_org],
                [76-x_org, 55-y_org, 3-z_org],
                [114-x_org, 55-y_org, 3-z_org]
            ];
    // [-8, -6, 2],
    // [-8, -6, 3],
    // [-8, -6, 4],
    // [-8, -6, 5],
    // [-8, -6, 6],
    // [-8, -6, 7],
    // [-8, -6, 8],
    // [-8, -6, 9],
    // [-8, -7, 9],
    // [-8, -8, 9],
    // [-8, -9, 9],
    // [-8, -10, 9],
    // [-8, -11, 9],
    // [-8, -12, 9],
    // [-8, -13, 9],
    // [-8, -14, 9],
    // [-8, -15, 9],
    // [-8, -16, 9],
    // [-8, -17, 9],
    // [-8, -18, 9],
    // [-9, -18, 9],
    // [-10, -18, 9],
    // [-11, -18, 9],
    // [-12, -18, 9],
    // [-13, -18, 9],
    // [-14, -18, 9],
    // [-15, -18, 9],
    // [-16, -18, 9],
    // [-17, -18, 9],
    // [-18, -18, 9],
    // [-19, -18, 9],
    // [-20, -18, 9],
    // [-21, -18, 9],
    // [-22, -18, 9],
    // [-23, -18, 9],
    // [-24, -18, 9],
    // [-25, -18, 9],
    // [-26, -18, 9],
    // [-27, -18, 9],
    // [-28, -18, 9],
    // [-29, -18, 9],
    // [-30, -18, 9],
    // [-31, -18, 9],
    // [-32, -18, 9],
    // [-33, -18, 9],
    // [-34, -18, 9],
    // [-35, -18, 9],
    // [-36, -18, 9],
    // [-37, -18, 9],
    // [-37, -18, 8],
    // [-37, -18, 7],
    // [-37, -18, 6],
    // [-37, -18, 5],
    // [-37, -18, 4],
    // [-37, -18, 3],
    // [-37, -18, 2],
    // [-37, -18, 1],
    // [-37, -18, 0],
    // [-37, -18, -1],
    // [-37, -18, -2],
    // [-37, -18, -3],
    // [-37, -18, -4],
    // [-37, -18, -5],
    // [-37, -18, -6],
    // [-37, -18, -7],
    // [-37, -18, -8],
    // [-37, -18, -9],
    // [-37, -18, -10],
    // [-37, -18, -11],
    // [-37, -18, -12],
    // [-37, -18, -13],
    // [-37, -17, -13],
    // [-37, -16, -13],
    // [-37, -15, -13],
    // [-37, -14, -13],
    // [-37, -13, -13],
    // [-37, -12, -13],
    // [-37, -11, -13],
    // [-37, -10, -13]]
     
    // changeOrigin(path_list);
    let THREE=window.THREE
    for (let index = 0; index < path_list.length; index++) {
    let element=path_list[index]
    var geometry = new THREE.BoxGeometry(1,1,1);
    var material = new THREE.MeshBasicMaterial({ color: 0xfe00ab});
    var cube = new THREE.Mesh(geometry, material);
    cube.position.set(element[0],element[1],element[2]);
    scene.add(cube)
    }
}
getGridData();