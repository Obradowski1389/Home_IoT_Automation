import { Component, ViewChild } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { ServiceService } from '../service/service.service';
import { WebsocketService } from '../service/websocket.service';

@Component({
  selector: 'app-wake-up',
  templateUrl: './wake-up.component.html',
  styleUrls: ['./wake-up.component.css']
})
export class WakeUpComponent {

  constructor(private dialogRef: MatDialogRef<WakeUpComponent>, private service: ServiceService) { }
  
  ngOnInit(){
  }

  close(){
    this.service.turnOffWakeUp().subscribe({
      next: data => this.dialogRef.close(),
      error: error => console.error('There was an error!', error)
    });
  }

}
