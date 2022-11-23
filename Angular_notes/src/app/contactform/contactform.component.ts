import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'contactform',
  templateUrl: './contactform.component.html',
  styleUrls: ['./contactform.component.css']
})
export class ContactformComponent implements OnInit
{
  log(x:any){console.log(x);}

  constructor() { }

  ngOnInit(): void {
  }

}
