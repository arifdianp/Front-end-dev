//first part of typescript
function log(message)
{
  console.log(message);
}
var message = "hello wrold";

//2nd part of typescript use let instead of var because i can be outside the curly
function dosth()
{
  for(let i=0; i<5; i++)
  {
    console.log(i);
  }
  console.log("finally");
}
dosth();

//simpler way to assign array var using enum
enum color{red = 0, blue = 1, yellow = 2};
let bgcolor = color.blue;

//simple way to write function in typescript
let dolog = (msg) => console.log(msg);

//properties class import from point.ts
import { Point2d } from './point';
let point = new Point2d(1,2);
point.draw();
let x = point.get_x();
