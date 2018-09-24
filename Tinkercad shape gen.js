
//intersect / combine

// Convenience Declarations For Dependencies.
// 'Core' Is Configured In Libraries Section.
// Some of these may not be used by this example.
var Conversions = Core.Conversions;
var Debug = Core.Debug;
var Path2D = Core.Path2D;
var Point2D = Core.Point2D;
var Point3D = Core.Point3D;
var Matrix2D = Core.Matrix2D;
var Matrix3D = Core.Matrix3D;
var Mesh3D = Core.Mesh3D;
var Plugin = Core.Plugin;
var Tess = Core.Tess;
var Sketch2D = Core.Sketch2D;
var Solid = Core.Solid;
var Vector2D = Core.Vector2D;
var Vector3D = Core.Vector3D;

var exit;

var startTime = 0;
var testName = "";

// Template Code:
params = [
    { "id": "r", "displayName": "Radius", "type": "length", "rangeMin": 1.0, "rangeMax": 100.0, "default": 25.0 }
];

function shapeGeneratorEvaluate(params, callback) {
  
    exit = callback;
    var r = params["r"];
    var ndivs = Tess.circleDivisions(r);
    var tau = 0.8506508084;
    var one = 0.5257311121;
    var lod = 0;

    while(ndivs > 6){
        lod++;
        ndivs /= 2;
    }

  Debug.log(" Tess Circle Divisions: " +  Tess.circleDivisions(r) + " lod: " + lod);

    var v = [
        [ tau, one, 0.0 ],
        [-tau, one, 0.0 ],
        [-tau,-one, 0.0 ],
        [ tau,-one, 0.0 ],
        [ one, 0.0, tau ],
        [ one, 0.0,-tau ],
        [-one, 0.0,-tau ],
        [-one, 0.0, tau ],
        [ 0.0, tau, one ],
        [ 0.0,-tau, one ],
        [ 0.0,-tau,-one ],
        [ 0.0, tau,-one ]
    ];
    
    var tris = [
        [ v[4], v[8], v[7] ],
        [ v[4], v[7], v[9] ],
        [ v[5], v[6],v[11] ],
        [ v[5],v[10], v[6] ],
        [ v[0], v[4], v[3] ],
        [ v[0], v[3], v[5] ],
        [ v[2], v[7], v[1] ],
        [ v[2], v[1], v[6] ],
        [ v[8], v[0],v[11] ],
        [ v[8],v[11], v[1] ],
        [ v[9],v[10], v[3] ],
        [ v[9], v[2],v[10] ],
        [ v[8], v[4], v[0] ],
        [v[11], v[0], v[5] ],
        [ v[4], v[9], v[3] ],
        [ v[5], v[3],v[10] ],
        [ v[7], v[8], v[1] ],
        [ v[6], v[1],v[11] ], 
        [ v[7], v[2], v[9] ],
        [ v[6],v[10], v[2] ]
    ];
    
    function norm(a) {
        var l = Math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2]);
        return [ a[0]/l, a[1]/l, a[2]/l ];
    }

    function sum(a, b) {
        return [ (a[0]+b[0]), (a[1]+b[1]), (a[2]+b[2]) ];
    }

    function xf(a, s) {
        return [ a[0]*s, a[1]*s, a[2]*s + s ];
    }
    
    for (var i = 0; i < lod; i++) {
        var ntris = [];
        for(var j = 0; j < tris.length; j++) {
            var ma = norm(sum(tris[j][0], tris[j][1]));
            var mb = norm(sum(tris[j][1], tris[j][2]));
            var mc = norm(sum(tris[j][2], tris[j][0]));
 
            ntris.push([tris[j][0], ma, mc]);
            ntris.push([tris[j][1], mb, ma]);
            ntris.push([tris[j][2], mc, mb]);
            ntris.push([ma, mb, mc]);
        }
        tris = ntris;
    }

    var sphere = new Mesh3D();
    for (i = 0; i < tris.length; i++)
        sphere.triangle(xf(tris[i][0],r), xf(tris[i][1],r), xf(tris[i][2],r));
  

  var cube = cubeMesh(40);
  
  var cube2 = cubeMesh(20);
  var tm = new Matrix3D().identity();
  tm.translation(30, 0, -10);
  cube2.transform(tm);
  
  var cube3 = cubeMesh(20);
  tm.identity().translation(-20, -20, -10);  
  cube3.transform(tm);
  
  //cube.combine(sphere);
  //cube.combine(cube2); 
  //cube.combine(cube3);
  cube.combine([sphere, cube2, cube3]); 
  exit(Solid.make(cube));
  
 //cube.flipNormals();
  
 // startTest("combine"); 
 // cube.combine(sphere); // Sync, dosent care about normals, boolean OR (keeping hull) 11ms
 // endTest();  
 // exit(Solid.make(cube));
  
 // startTest("subtract");
 // cube.subtract(sphere, function(m) { next(m); } ); // Async, boolean (cube - sphere) 2700ms
  
 // startTest("unite");
 // cube.unite(sphere, function(m) { next(m); } ); // Async, boolean OR 2600ms
  
 // startTest("intersect");
 // cube.intersect(sphere, function(m) { next(m); } ); // Async, boolean AND 1500ms
  
  
}


function cubeMesh(width) {
  var result =  new Mesh3D();
  var cw = width / 2;
  
  var trf = [ cw, -cw, cw ];
  var trb = [ cw, cw, cw ];
  var tlf = [ -cw, -cw, cw ];
  var tlb = [ -cw, cw, cw ];
  
  var brf = [ cw, -cw, -cw ];
  var brb = [ cw, cw, -cw ];
  var blf = [ -cw, -cw, -cw ]; 
  var blb = [ -cw, cw, -cw ];
  
  
  result.quad( trf, trb, tlb, tlf); // top
  
  result.quad( brf, blf, blb, brb); // bottom
  
  result.quad( trf, tlf, blf, brf); // front
    
  result.quad( trb, brb, blb, tlb); // back  
  
  result.quad( trf, brf, brb, trb); // right
  
  result.quad( tlf, tlb, blb, blf); // left 

  return result;
}

function next(mesh) {
  endTest();
  exit(Solid.make(mesh));
}

function startTest(name) {
  testName = name;
  startTime = Date.now();
}

function endTest() {
  var endTime = Date.now();
  Debug.log(testName + ": " + (endTime - startTime) + " ms");
}





// s2m 2018-09-23

// Convenience Declarations For Dependencies.
// 'Core' Is Configured In Libraries Section.

var Conversions = Core.Conversions;
var Debug = Core.Debug;
var Path2D = Core.Path2D;
var Point2D = Core.Point2D;
var Point3D = Core.Point3D;
var Matrix2D = Core.Matrix2D;
var Matrix3D = Core.Matrix3D;
var Mesh3D = Core.Mesh3D;
var Plugin = Core.Plugin;
var Tess = Core.Tess;
var Sketch2D = Core.Sketch2D;
var Solid = Core.Solid;
var Vector2D = Core.Vector2D;
var Vector3D = Core.Vector3D;

params = [
    { "id": "n", "displayName": "Number of Teeth", "type": "int", "rangeMin": 4, "rangeMax": 300, "default": 20 },
    { "id": "height", "displayName": "Thickness", "type": "length", "rangeMin": 0.0, "rangeMax": 100.0, "default": 20.0 },
    { "id": "hole", "displayName": "Center hole Dia", "type": "length", "rangeMin": 0.0, "rangeMax": 100.0, "default": 8.0 },
   
    { "id": "edge", "displayName": "Edge Chamfer", "type": "float", "rangeMin": 0.0, "rangeMax": 0.5, "default": 0.15 },
    { "id": "adj", "displayName": "Inward Adjust", "type": "float", "rangeMin": -0.5, "rangeMax": 0.5, "default": 0.0 },
    { "id": "od_adj", "displayName": "OD Adjust", "type": "float", "rangeMin": -0.5, "rangeMax": 0.5, "default": 0.0 }

];

    var exit; // Async callback exit function

    var pitch = 2.00; // S2M params
    var edgeRad = 0.15;

    var dPI = Math.PI*2;

    // User input params
    var n;
    var height;  
    var adj;  
    var holeDia;
    var od_adj;

    // Computed params 
    var pd;
    var od;
    var bd;
    var halfToothAngle;


//Entry point
function shapeGeneratorEvaluate(params, callback) {
  
    // Get and save parameters  
    exit = callback;
  
    n = params["n"];
    height = params["height"];  
    adj = params["adj"];
    holeDia = params["hole"];
    edgeRad = params["edge"];
    od_adj = params["od_adj"];
  
    // Compute base parameters
    pd = n * pitch / Math.PI; // pitch diameter
    od = pd - (0.254 * 2); //5138; // outside diameter
    bd = od - (0.76 * 2);   // base diameter
    bd = bd - (adj*2);

    halfToothAngle = Math.PI / n;  
  
Debug.log("Step 1, inputs, gen tooth section, involute, radius"); 
Debug.log("n: " + n);
Debug.log("pd: " + pd);
Debug.log("od: " + od);
Debug.log("bd: " + bd);   
  
    //create half Tooth circle segment 
  
    var cl = [0, 0, 0];
    var pl = [0, (od + od_adj) / 2.0, 0];   
  
    var RH_tooth = cylinderSection( (od + od_adj) / 2.0, height, dPI-halfToothAngle, dPI, 3);
  
    //create round "involute" style cuttter at offset 

    var invCyl = cylinderSection(1.325 + adj, height, Math.PI, 1.5*Math.PI, 6);
    var tm = new Matrix3D().identity().translation(1.30 /2, (od / 2) + 0.172, 0); 
    invCyl.transform(tm);

  
    //tooth point "radius"
  
    var extendedEdge = edgeRad * 1.5; // to overlap the involute radius
   // var extendedEdgeOffset = edgeRad * 2; 
    
    var inter = intersectTwoCircles(0, 0, od/2, 1.30 /2, (od / 2) + 0.172, 1.325 + adj);
    if (inter[1][0] < inter[0][0]) inter[0] = inter[1]; // just to be sure
  
    var rad = wedge([extendedEdge, -extendedEdge, 0],
                    [-extendedEdge, extendedEdge, 0],
                    [extendedEdge, extendedEdge, 0],
                    height); 
  
    tm.identity().rotationZ(halfToothAngle);  
    rad.transform(tm);   
      
    tm.identity().translation(inter[0][0]-(0.5*edgeRad), inter[0][1]-(0.5*edgeRad), 0);
    rad.transform(tm); 
  
    //cut the half segment with involute and radius
    RH_tooth.subtract([invCyl,rad], function(m) { step2(m); } ); 
}

function step2(mesh) {
Debug.log("Step 2, base diameter");  
  
  var base = cylinderSection( bd / 2.0, height, dPI-halfToothAngle, dPI, 3);
  mesh.unite(base, function(m) { step3(m); } );    
}

function step3(mesh) {  
Debug.log("in step 3, center hole" );
  
    var centHole = cylinder(holeDia/2, height);     
    mesh.subtract(centHole, function(m) { step4(m); } );   
}

function step4(mesh) {
Debug.log("in step 4, copy and paste" );

    var tm = new Matrix3D().identity(); 
    var nextTooth = mesh.clone();
  
    tm.identity();    
    for (var i = 1; i < n; ++i) {
        tm.rotationZ(halfToothAngle*2);
        nextTooth.transform(tm);
        mesh.combine(nextTooth);
    }

    var mirTooth = mesh.clone();
    tm.identity().scaling(-1, 1, 1); // flip along X  
    mirTooth.transform(tm).flipNormals();    
  
    mesh.unite(mirTooth, function (m) { exit(Solid.make(m)); } );
}

function cylinder(r, height) {
    var cl = [0,0,0];
    var ch = [0,0, height];
    var pl = [r,0,0];
    var ph = [r,0,height];
  
    var ndivs = Tess.circleDivisions(r)*2;
    
    var mesh = new Mesh3D();
    for (var i = 0; i < ndivs; i++) {
        var a = (i+1)/ndivs * Math.PI*2;
        var s = Math.sin(a);
        var c = Math.cos(a);
        var nl = [r*c, -r*s, 0];
        var nh = [r*c, -r*s, height];
        mesh.triangle(pl, ph, nl);
        mesh.triangle(nl, ph, nh);
        mesh.triangle(cl, pl, nl);
        mesh.triangle(ch, nh, ph);
        pl = nl;
        ph = nh;
    }

  return mesh;
}


function cylinderSection( r, height, startAngle, endAngle, ndivs) {

    var mesh = new Mesh3D();
  
    var cl = [0,0,0];
    var ch = [0,0, height];
  
    var pl = rotateZ([0, r, 0], -startAngle);
    var ph = [pl[0], pl[1], height];
  
    mesh.quad(cl, ch, ph, pl); // starting pane
  
    if (! ndivs) ndivs = 10;
    var a = -(endAngle - startAngle) / ndivs;
  
    for (var i = 0; i < ndivs; i++) {
      
        var nl = rotateZ(pl, a);
        var nh = [nl[0], nl[1], height]; 
       
        mesh.quad(pl, ph, nh, nl); //side
        mesh.triangle(cl, pl, nl); //bottom slice
        mesh.triangle(ch, nh, ph); //top slice 
      
        pl = nl;
        ph = nh;
    }
  
    mesh.quad(cl, pl, ph, ch); // ending pane

    return mesh;  
}



function rotateZ(pts, a) {
    var s = Math.sin(a);
    var c = Math.cos(a);
  
    var x = (pts[0] * c) - (pts[1] * s);
    var y = (pts[0] * s) + (pts[1] * c);
    return [x, y, pts[2]];  
}

// viewed from top
//  p2---p3
//   \   |
//    \  |
//     \ |
//      p1
//
function wedge(p1, p2, p3, h) {

    var res = new Mesh3D();
  
    var p1h = [p1[0], p1[1], p1[2] + h];
    var p2h = [p2[0], p2[1], p2[2] + h];
    var p3h = [p3[0], p3[1], p3[2] + h];
  
    res.triangle(p1, p2, p3); // bottom
    res.triangle(p1h, p3h, p2h); // top

    res.quad(p1, p3, p3h, p1h); // middle
    res.quad(p1, p1h, p2h, p2); // left
    res.quad(p3, p2, p2h, p3h); // out

    return res; 
}


// based on the math here:
// http://math.stackexchange.com/a/1367732
// https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac
// x1,y1 is the center of the first circle, with radius r1
// x2,y2 is the center of the second ricle, with radius r2
function intersectTwoCircles(x1,y1,r1, x2,y2,r2) {
  var centerdx = x1 - x2;
  var centerdy = y1 - y2;
  var R = Math.sqrt(centerdx * centerdx + centerdy * centerdy);
  if (!(Math.abs(r1 - r2) <= R && R <= r1 + r2)) { // no intersection
    return []; // empty list of results
  }
  // intersection(s) should exist 

  var R2 = R*R;
  var R4 = R2*R2;
  var a = (r1*r1 - r2*r2) / (2 * R2);
  var r2r2 = (r1*r1 - r2*r2);
  var c = Math.sqrt(2 * (r1*r1 + r2*r2) / R2 - (r2r2 * r2r2) / R4 - 1);

  var fx = (x1+x2) / 2 + a * (x2 - x1);
  var gx = c * (y2 - y1) / 2;
  var ix1 = fx + gx;
  var ix2 = fx - gx;

  var fy = (y1+y2) / 2 + a * (y2 - y1);
  var gy = c * (x1 - x2) / 2;
  var iy1 = fy + gy;
  var iy2 = fy - gy;

  // note if gy == 0 and gx == 0 then the circles are tangent and there is only one solution
  // but that one solution will just be duplicated as the code is currently written
  return [[ix1, iy1], [ix2, iy2]];
}


