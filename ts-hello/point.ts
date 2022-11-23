export class Point2d
{
  constructor(private x?:number, private y?:number){}

  draw()
  {
    console.log("x = " + this.x + " y = " + this.y);
  }

  get_x()
  {
    return this.x;
  }
}
