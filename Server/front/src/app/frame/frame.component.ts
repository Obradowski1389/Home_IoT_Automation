import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-frame',
  templateUrl: './frame.component.html',
  styleUrls: ['./frame.component.css']
})
export class FrameComponent {
  id: number = 0;

  url: string = "http://localhost:3000/d-solo/dek3gg04ng7b4f/rdht1?orgId=1&from=1745687756669&to=1745688056669&timezone=browser&panelId="

  constructor(@Inject(MAT_DIALOG_DATA) data: any){
    this.id = data.id;
    this.url += this.id;
  }

}
