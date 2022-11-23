//import courses Component
import { Coursescomponent } from './courses.component';
import { Coursesservice } from './courses.service';

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule, routingComponents } from './app-routing.module';
import { AppComponent } from './app.component';
import { ContactformComponent } from './contactform/contactform.component';

@NgModule({
  // add courses component here or in cmd type 'ng g c courses'
  declarations: [
    AppComponent,
    routingComponents
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
  ],
  providers: [Coursesservice],
  bootstrap: [AppComponent]
})
export class AppModule { }
