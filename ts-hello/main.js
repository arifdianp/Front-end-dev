"use strict";
exports.__esModule = true;
//first part of typescript
function log(message) {
    console.log(message);
}
var message = "hello wrold";
//2nd part of typescript use let instead of var because i can be outside the curly
function dosth() {
    for (var i = 0; i < 5; i++) {
        console.log(i);
    }
    console.log("finally");
}
dosth();
//simpler way to assign array var using enum
var color;
(function (color) {
    color[color["red"] = 0] = "red";
    color[color["blue"] = 1] = "blue";
    color[color["yellow"] = 2] = "yellow";
})(color || (color = {}));
;
var bgcolor = color.blue;
//simple way to write function in typescript
var dolog = function (msg) { return console.log(msg); };
//properties class import from point.ts
var point_1 = require("./point");
var point = new point_1.Point2d(1, 2);
point.draw();
var x = point.get_x();
