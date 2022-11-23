"use strict";
exports.__esModule = true;
exports.Point2d = void 0;
var Point2d = /** @class */ (function () {
    function Point2d(x, y) {
        this.x = x;
        this.y = y;
    }
    Point2d.prototype.draw = function () {
        console.log("x = " + this.x + " y = " + this.y);
    };
    Point2d.prototype.get_x = function () {
        return this.x;
    };
    return Point2d;
}());
exports.Point2d = Point2d;
