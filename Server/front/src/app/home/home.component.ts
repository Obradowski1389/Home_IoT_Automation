import { Component } from '@angular/core';
import { MatDialog, MatDialogConfig, MatDialogRef } from '@angular/material/dialog';
import { RgbComponent } from '../rgb/rgb.component';
import { ClockComponent } from '../clock/clock.component';
import { WakeUpComponent } from '../wake-up/wake-up.component';
import { WebsocketService } from '../service/websocket.service';
import { AlarmComponent } from '../alarm/alarm.component';
import { FrameComponent } from '../frame/frame.component';
import { ServiceService } from '../service/service.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {

  alarmDialog!: MatDialogRef<AlarmComponent>;
  peopleCount: number = 0;
  alarmNoted: boolean = false;

  currTemp: String = "20";
  currTempInside: String = "20";

  windowState: String = "CLOSED";
  systemState: String = "ON";
  
  isChangingMode: boolean = false;

  selectedMode: number = 0;    // 0 = Auto, 1 = Manual, 2 = Economy
  modeText: string = 'Auto';

  fanSpeed: number = 1;        // Fan speed (only for Manual mode)
  temperature: number = 22;    // Temperature value (only for Auto/Economy)
  continualParam1: number = 0;
  continualParam2: number = 0;
  continualParam3: number = 0;
  continualParam4: String = "0";
  fanSpeedActual: number = 0;
  
  
  constructor(private wsService: WebsocketService, private dialog: MatDialog, private service: ServiceService){}

  dialogConfig = new MatDialogConfig();
  
  ngOnInit(): void {
    this.dialogConfig.disableClose = false;
    this.dialogConfig.autoFocus = true;
    this.dialogConfig.closeOnNavigation = true;
    this.dialogConfig.width = '30%';
    this.dialogConfig.height = 'auto';


    this.wsService.connect().then(() => {
      this.wsService.subscribeWakeUpTopic((message: any) => {
        console.log("wake up");
        this.wakeUp();
      });
      
      this.wsService.subscribeAlarmTopic((message: any) => {
        if(message["alarm"] == 1) {
          if(!this.alarmNoted) { 
          this.alarm();
          }
        }
        else this.alarmDialog.close();
      });

      this.wsService.subscribeliveTemperatureTopic((message: any) => {
        this.currTemp = parseFloat(message["temp"]).toFixed(1);
      });

      this.wsService.subscribSystemStateTopic((message: any) => {
        if (message["state"]==1) {
        this.systemState = "ON"
      } else {
        this.systemState = "OFF"
      }
      });

      this.wsService.subscribeliveInsideTemperatureTopic((message: any) => {
        this.currTempInside = parseFloat(message["temp"]).toFixed(1);
      });

      this.wsService.subscribeToWindowTopic((message: any) => {
        console.log(message["window"])
        if (message["window"]==1) {
          this.windowState = "OPEN"
        } else {
          this.windowState = "CLOSED"
        }
      });

      this.wsService.subscribeToProcenatTopic((message: any) => {
        // if (this.continualParam4 != "0") {
        this.continualParam4 = parseFloat(message["procenat"]).toFixed(1);
        // }
      });

      this.wsService.subscribeToActualFanSpeedTopic((message: any) => {
        console.log("brzinaa" + message["speed"])
        this.fanSpeedActual = message["speed"]
      });

      this.wsService.subscribeToTypeStateTopic((message: any) => {
        // if (this.isChangingMode) {
        //   console.log('Ignoring backend update while user is changing mode.');
        //   return;
        // }
      
        // this.selectedMode = message["state"];
        // const labels = ['Auto', 'Manual', 'Continual'];
        // this.modeText = labels[this.selectedMode];

      });

      this.wsService.subscribeToPIDTopic((message: any) => {
        if (this.continualParam1 == 0) {
          console.log(message)
          this.continualParam1 = message["kp"];
          this.continualParam2 = message["ki"];
          this.continualParam3 = message["kd"];
        }
      });


      this.wsService.subscribePeopleCountTopic((message: any) => {
        this.peopleCount = message["people_count"];
      });
    }).catch((error: any) => {
      console.error('Error connecting to WebSocket:', error);
    });
  
  }

  openClockDialog(){
    this.dialogConfig.width = '35%';
    this.dialog.open(ClockComponent, this.dialogConfig);
    this.dialogConfig.width = '30%';

  }

  openRGBDialog(){
    this.dialog.open(RgbComponent, this.dialogConfig);

  }

  wakeUp(){
    this.dialog.open(WakeUpComponent, this.dialogConfig);
  }

  alarm(){
    this.dialogConfig.width = 'auto';
    this.alarmDialog = this.dialog.open(AlarmComponent, this.dialogConfig);
    this.dialogConfig.width = '30%';
    this.alarmNoted = true;
  }

  openFrame(id: number){
    this.dialogConfig.width = 'auto';
    this.dialogConfig.data = {id: id};
    this.dialog.open(FrameComponent, this.dialogConfig);
    this.dialogConfig.width = '30%';
  }

  onModeChange(): void {
    const labels = ['Auto', 'Manual', 'Continual'];
    // this.modeText = labels[this.selectedMode];
    // this.isChangingMode = true;

    // console.log('Mode changed to:', this.modeText);
    
    // Optionally send initial values
    if (this.selectedMode === 1) {
      this.sendFanSpeed();
    } else {
      this.sendTemperature(this.selectedMode);
    }
    // setTimeout(() => {
    //   this.isChangingMode = false; 
    // }, 2000); // adjust timeout if needed
    this.alarmNoted = false;
  }
  
  onFanSpeedChange(): void {
    console.log('Fan speed set to:', this.fanSpeed);
    this.sendFanSpeed();
  }
  
  onTemperatureChange(): void {
    console.log('Temperature set to:', this.temperature, '°C');
    this.sendTemperature(this.selectedMode+1);
  }
  
  private sendFanSpeed(): void {
    console.log("inin")
    this.service.sendFanSpeed(this.fanSpeed);
  }
  
  private sendTemperature(mode: number): void {
    this.service.sendTemperature(this.temperature, mode);
  }

  sendContinualMode() {
    const payload = {
      param1: this.continualParam1,
      param2: this.continualParam2,
      param3: this.continualParam3,
      param4: this.continualParam4
    };
    this.service.sendPID(payload);
  }

  onSystemStateClick(): void {
    console.log('System State clicked:', this.systemState);
    if (this.systemState == "ON") {
      this.service.changeSystemState(false);
      this.systemState = "OFF";
    } else {
      this.service.changeSystemState(true);
      this.systemState = "ON";
    }
  }
}
