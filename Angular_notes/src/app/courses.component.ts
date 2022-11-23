import { Coursesservice } from './courses.service';
import { Component } from '@angular/core';

@Component({
  selector: 'courses',
  template: `
  <h2>{{ title }}</h2>
  <ul>
    <li *ngFor = "let course of courses">{{course}}</li>
  </ul>
  `
})

export class Coursescomponent
{
  title = "list of courses";
  courses;

  constructor(service: Coursesservice)
  {
    this.courses = service.getCourses();
  }
}
