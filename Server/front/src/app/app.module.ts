import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { DhtComponent } from './dht/dht.component';
import { HomeComponent } from './home/home.component';
import { MaterialModule } from 'src/infrastructure/material/material.module';
import { RgbComponent } from './rgb/rgb.component';
import { ClockComponent } from './clock/clock.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { WakeUpComponent } from './wake-up/wake-up.component';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AlarmComponent } from './alarm/alarm.component';
import { FrameComponent } from './frame/frame.component';
import { SafePipe } from './pipe/safe.pipe';

@NgModule({
  declarations: [
    AppComponent,
    DhtComponent,
    HomeComponent,
    RgbComponent,
    ClockComponent,
    WakeUpComponent,
    AlarmComponent,
    FrameComponent,
    SafePipe
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MaterialModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
