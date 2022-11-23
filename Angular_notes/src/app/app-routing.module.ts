import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { Coursescomponent } from './courses.component';
import { ContactformComponent } from './contactform/contactform.component';

const routes: Routes = [
  { path : 'courses', component : Coursescomponent},
  { path : 'contact', component : ContactformComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
export const routingComponents = [Coursescomponent, ContactformComponent];
