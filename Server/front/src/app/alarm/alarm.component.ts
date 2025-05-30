import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { ServiceService } from '../service/service.service';

@Component({
  selector: 'app-alarm',
  templateUrl: './alarm.component.html',
  styleUrls: ['./alarm.component.css']
})
export class AlarmComponent {
  constructor(private dialogRef: MatDialogRef<AlarmComponent>, private service: ServiceService){}

  turnOff(){
    this.service.turnOffAlarm().subscribe({
      next: (data: any) => this.dialogRef.close(),
      error: (error: any) => console.log(error)
    });
  }
}
