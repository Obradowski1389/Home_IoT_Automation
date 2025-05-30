import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environment/environment';

@Injectable({
  providedIn: 'root'
})
export class ServiceService {

  constructor(private http: HttpClient) { }

  setWakeUpTime(time: any){
    return this.http.get(environment.apiHost + 'api/set_wakeup_time?time='+time);
  }

  turnOffWakeUp(){
    return this.http.get(environment.apiHost + 'api/turn_off_wakeup');
  }

  change_rgb_color(color: any){
    return this.http.put(environment.apiHost + 'api/change_rgb', {"color": color});
  }

  turnOffAlarm(){
    return this.http.get(environment.apiHost + 'api/turn_off_alarm');
  }

  sendFanSpeed(fanSpeed: number) {
    return this.http.put(environment.apiHost + 'api/fanSpeed', { "fanSpeed": fanSpeed}).subscribe(response => {
      console.log(response)
    })
  }

  sendTemperature(temp: number, mode:number) {
    return this.http.put(environment.apiHost + 'api/temp', {"temp": temp, "mode": mode}).subscribe(response => {
      console.log(response)
    })
  }

  sendPID(pid: any) {
    return this.http.put(environment.apiHost + "api/PID", pid).subscribe(response => {
      console.log(response);
    })
  }

  changeSystemState(state: boolean) {
    return this.http.put(environment.apiHost + "api/systemState", {"state": state}).subscribe(response => {
      console.log(response);
    })
  }
}
