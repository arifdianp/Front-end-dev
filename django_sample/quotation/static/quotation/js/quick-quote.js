$(document).ready(function(){

/////////////////////////////////////////////////////DROPZONE/////////////////////////////////////////////////////////////////////

    $("#my-awesome-dropzone").dropzone({
        url: "/upload-files/",
        paramName: "model3d_file", // The name that will be used to transfer the file
        maxFilesize: 5, // MB
        // createImageThumbnails: false,
        clickable: true,
        acceptedFiles:".stl,.sldprt,.step",
        accept: function(file, done) {
            if (file.name == "justin.jpg") {
              done("Naha, you don't.");
            }
            else { done(); }
        },
        init: function () {
            this.on("sending", function(file, xhr, formData) {
               formData.append("csrfmiddlewaretoken", csrftoken);
               $("#loading").show();
            });
            this.on('complete', function () {
                // location.reload();
                $("#loading").hide();

            });
            this.on("success", function(file, response) {
                console.log("response status code:"+response.status_code);
                console.log("result:"+response.result);
                var filepath = response.filepath;
                // var template = $('#hidden-template').html();
                var $template = $("#model-");
                var model_id = response.model_id;
                var model_filepath = response.filepath;
                var model_filename = response.filename;
                var temp_list = model_filename.split("/");
                var model_filename_short = temp_list[temp_list.length -1];
                var model_filesize = response.filesize;
                var $new_model = $template.clone().prop('id',"model-" + model_id);

                console.log("NEW MODEL IS:");
                console.log($new_model);
                $new_model.css("display", "");

                $new_model.find(".canvas-container").attr("id", "canvas-container-" + model_id);
                $new_model.find(".stl-canvas").attr("id","stl-canvas-" + model_id);
                $new_model.find(".model-file-name").text(model_filename_short);
                $new_model.find("#carousel-model").attr("id","carousel-model-" + model_id);
                $new_model.find(".carousel-control-prev").attr("href","#carousel-model-" + model_id);
                $new_model.find(".carousel-control-next").attr("href","#carousel-model-" + model_id);
                // rename inputs
                $new_model.find("input[name='material-type']").each(function(){
                    $(this).attr("name", "material-type-" + model_id);
                });
                $new_model.find("input[name='manuf-process']").each(function(){
                    $(this).attr("name", "manuf-process" + model_id);
                });
                $new_model.find("input[name='notes']").each(function(){
                    $(this).attr("name", "notes" + model_id);
                });
                var model_dict = {};
                model_dict.id = model_id;
                model_dict.filepath = model_filepath;
                model_dict.filename = model_filename;
                model_dict.filesize = model_filesize;

                console.log("BALISE1:");
                console.log(model_dict);
                console.log($new_model.find(".model"));


                // $("#models-container").append($new_model);
                $new_model.insertBefore("#loading");
                $new_model.show("",init_model(filepath, model_id));
                // $new_model.find(".model").data("model", model_dict);

                // attach data to model
                $("#model-" + model_id).data("model", model_dict);
                $("#model-" + model_id).attr("data-object-id", model_id);

                // update listeners
                $("#model-" + model_id).find(".RadioBtn-label").tooltip();
                $(".RadioBtn-input").change(function(){UpdatePartData($(this));});
                $(".notes").change(function(){UpdatePartData($(this));});
                console.log("balise212");
                console.log($("#model-" + model_id).data())
                // init_model(filepath, model_id);
                // init(filepath);
            });

        },
    });
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////MODEL DATA UPDATE////////////////////////////////////////////////////////////////////////

    $(".RadioBtn-input").change(function(){UpdatePartData($(this));});
    $(".notes").change(function(){UpdatePartData($(this));});
    function UpdatePartData($input){
        // console.log("yes");
        // console.log("model is:");
        // console.log($input.closest(".single-model"));
        var $model = $input.closest(".single-model");
        var $carousel = $input.closest(".carousel");
        var model_data = $model.data("model");
        if (~$input.attr("name").indexOf("manuf-process")){
            model_data.manuf_process = $input.val();
            $model.data("model", model_data);
        };
        if (~$input.attr("name").indexOf("material-type")){
            model_data.material_type = $input.val();
            $model.data("model", model_data);
        };
        if (~$input.attr("name").indexOf("notes")){
            model_data.notes = $input.val();
            $model.data("model", model_data);
        };
        $carousel.carousel('next');
        console.log($model.data("model"));
    };


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////TOOLTIPS///////////////////////////////////////////////////////////////////////////
    $('[data-toggle="tooltip"]').tooltip();
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////3D MODEL///////////////////////////////////////////////////////////////////////////
function init_model(filepath, id_model){
    if ( ! Detector.webgl ) Detector.addGetWebGLMessage();
    			var container, stats;
    			var camera, cameraTarget, controls, scene, renderer;
                // var width = $("#stlcanvas").closest(".container").width();
                // var height = $("#stlcanvas").closest(".container").width();
                var width = $('#canvas-container-'+id_model).width();
                var height = $('#canvas-container-'+id_model).width();
                console.log("WIDTH IS: " + width);
                console.log("HEIGHT IS: " + height);
    			init();
    			animate();
    			function init() {
    				container = document.getElementById('stl-canvas-'+id_model)
                    console.log("CONTAINER IS : " + container)
    				// document.body.appendChild( container );
    				camera = new THREE.PerspectiveCamera( 35, width / height, 1, 1500 );
    				camera.position.set( 0, 0, 400 );
                    // camera.position.set( 217, -229, 133 );
                    // camera.rotation.set(1.04,0.68,0.2);
                    // camera.rotation.set(90 * Math.PI / 180,90 * Math.PI / 180,90 * Math.PI / 180);
                    // camera.rotation.y = 90 * Math.PI / 180;
                    // camera.rotation.z = 90 * Math.PI / 180;
                    // camera.position.set( 3, 0.15, 3 );
    				cameraTarget = new THREE.Vector3( 0, 0, -1 );
                    // cameraTarget = new THREE.Vector3( 0, -0.25, 0 );
    				scene = new THREE.Scene();
    				scene.background = new THREE.Color( 0x3d81db );
    				// scene.fog = new THREE.Fog( 0x72645b, 2, 15 );
                    // controls
                    controls = new THREE.TrackballControls( camera, container);
                    // controls.target.set( 0, 0, 0 );

    				// controls.rotateSpeed = 1.0;
    				// controls.zoomSpeed = 1.2;
    				// controls.panSpeed = 0.8;
                    // //
    				// controls.noZoom = false;
    				// controls.noPan = false;
                    // //
    				// controls.staticMoving = true;
    				// controls.dynamicDampingFactor = 0.3;
                    // //
    				// controls.keys = [ 65, 83, 68 ];

                    container.onclick = function(){
                        console.log("clicked");
                        // controls.addEventListener( 'change', render );
                    };




    				// Ground
    				var plane = new THREE.Mesh(
    					new THREE.PlaneBufferGeometry( 225, 145 ),
    					new THREE.MeshPhongMaterial( { color: 0x999999, specular: 0x101010 } )
    				);
    				plane.rotation.x = 0;
    				plane.position.y = 0;
                    // plane.rotation.x = -Math.PI/2;
    				// plane.position.y = -0.5;
    				scene.add( plane );
    				plane.receiveShadow = true;
    				// ASCII file
    				var loader = new THREE.STLLoader();
    				loader.load( filepath, function ( geometry ) {
    					var material = new THREE.MeshPhongMaterial( { color: 0xff5533, specular: 0x111111, shininess: 200 } );
    					var mesh = new THREE.Mesh( geometry, material );
    					mesh.position.set( 0, 0, 0 );
    					mesh.rotation.set( 0, 0, 0 );
    					mesh.scale.set( 1, 1, 1 );
    					mesh.castShadow = true;
    					mesh.receiveShadow = true;
    					scene.add( mesh );
    				} );
    				// BNIARY FILES
    				// var material = new THREE.MeshPhongMaterial( { color: 0xAAAAAA, specular: 0x111111, shininess: 200 } );
    				// loader.load( filepath, function ( geometry ) {
    				// 	var mesh = new THREE.Mesh( geometry, material );
    				// 	mesh.position.set( 0, - 0.37, - 0.6 );
    				// 	mesh.rotation.set( - Math.PI / 2, 0, 0 );
    				// 	mesh.scale.set( 2, 2, 2 );
    				// 	mesh.castShadow = true;
    				// 	mesh.receiveShadow = true;
    				// 	scene.add( mesh );
    				// } );
    				// loader.load( './models/stl/binary/pr2_head_tilt.stl', function ( geometry ) {
    				// 	var mesh = new THREE.Mesh( geometry, material );
    				// 	mesh.position.set( 0.136, - 0.37, - 0.6 );
    				// 	mesh.rotation.set( - Math.PI / 2, 0.3, 0 );
    				// 	mesh.scale.set( 2, 2, 2 );
    				// 	mesh.castShadow = true;
    				// 	mesh.receiveShadow = true;
    				// 	scene.add( mesh );
    				// } );

                    // COLORED BINARY STL
    				// loader.load( filepath, function ( geometry ) {
    				// 	var meshMaterial = material;
    				// 	if (geometry.hasColors) {
    				// 		meshMaterial = new THREE.MeshPhongMaterial({ opacity: geometry.alpha, vertexColors: THREE.VertexColors });
    				// 	}
    				// 	var mesh = new THREE.Mesh( geometry, meshMaterial );
    				// 	mesh.position.set( 0.5, 0.2, 0 );
    				// 	mesh.rotation.set( - Math.PI / 2, Math.PI / 2, 0 );
    				// 	mesh.scale.set( 0.3, 0.3, 0.3 );
    				// 	mesh.castShadow = true;
    				// 	mesh.receiveShadow = true;
    				// 	scene.add( mesh );
    				// } );

    				// Lights
    				scene.add( new THREE.HemisphereLight( 0x443333, 0x111122 ) );
    				addShadowedLight( 1, 1, 1, 0xffffff, 1.35 );
    				addShadowedLight( 0.5, 1, -1, 0xffaa00, 1 );

    				// renderer
    				renderer = new THREE.WebGLRenderer( { antialias: true } );
    				renderer.setPixelRatio( width/height );
    				renderer.setSize( width, height );
    				renderer.gammaInput = true;
    				renderer.gammaOutput = true;
    				renderer.shadowMap.enabled = true;
    				renderer.shadowMap.renderReverseSided = false;
    				container.appendChild( renderer.domElement );
    				// stats
    				// stats = new Stats();
    				// container.appendChild( stats.dom );
    				//
    				window.addEventListener( 'resize', onWindowResize, false );
    			}
    			function addShadowedLight( x, y, z, color, intensity ) {
    				var directionalLight = new THREE.DirectionalLight( color, intensity );
    				directionalLight.position.set( x, y, z );
    				scene.add( directionalLight );
    				directionalLight.castShadow = true;
    				var d = 1;
    				directionalLight.shadow.camera.left = -d;
    				directionalLight.shadow.camera.right = d;
    				directionalLight.shadow.camera.top = d;
    				directionalLight.shadow.camera.bottom = -d;
    				directionalLight.shadow.camera.near = 1;
    				directionalLight.shadow.camera.far = 4;
    				directionalLight.shadow.mapSize.width = 1024;
    				directionalLight.shadow.mapSize.height = 1024;
    				directionalLight.shadow.bias = -0.005;
    			}
    			function onWindowResize() {
                    var width = $('#canvas-container-'+id_model).width();
                    var height = $('#canvas-container-'+id_model).width();
                    console.log("RESIZE WIDTH: "+ width);
                    console.log("RESIZE HEIGHT: "+ height);
    				camera.aspect = width / height;
    				camera.updateProjectionMatrix();
                    controls.handleResize();
    				renderer.setSize( width, height );
    			}
    			function animate() {
    				requestAnimationFrame( animate );
                    controls.update();
    				render();
    				// stats.update();
    			}
    			function render() {
    				// var timer = Date.now() * 0.0005;
    				// camera.position.x = Math.cos( timer ) * 3;
    				// camera.position.z = Math.sin( timer ) * 3;
    				camera.lookAt( cameraTarget );
                    // camera.rotation.x = 90 * Math.PI / 180;
                    // console.log("CAMERA X: " + camera.position.x);
                    // console.log("CAMERA Y: " + camera.position.y);
                    // console.log("CAMERA Z: " + camera.position.z);
                    // console.log("CAMERA RX: " + camera.rotation.x);
                    // console.log("CAMERA RY: " + camera.rotation.y);
                    // console.log("CAMERA RZ: " + camera.rotation.z);
    				renderer.render( scene, camera );
    			}
            };
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


});
