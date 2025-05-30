import { Component } from '@angular/core';
import { ServiceService } from '../service/service.service';
import { WebsocketService } from '../service/websocket.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-clock',
  templateUrl: './clock.component.html',
  styleUrls: ['./clock.component.css']
})
export class ClockComponent {

  constructor(private service: ServiceService, private wsService: WebsocketService, private snackBar: MatSnackBar){}

  currentTime: Date = new Date();
  alarm: Date | null = null;

  ngOnInit(): void {
    this.alarm = JSON.parse(localStorage.getItem('alarm') || '{}');
  }

  ngAfterViewInit(): void {
    setInterval(() => {
      this.currentTime = new Date();
    }, 10000);
  }

  save() {
    console.log('Selected time:', this.alarm);
    localStorage.setItem('alarm', JSON.stringify(this.alarm));
    this.service.setWakeUpTime(this.alarm).subscribe((data: any) => {
      console.log(data);
      this.snackBar.open('Alarm set to ' + this.alarm, 'Close', {
        duration: 2000,
      });
    });
  }

  reset(){
    this.alarm = null
  }

}
