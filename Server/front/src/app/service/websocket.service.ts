import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';


@Injectable({
  providedIn: 'root'
})
export class WebsocketService {

  private socket: Socket;

  constructor() {
    this.socket = io('http://localhost:5000'); // Connect to Flask-SocketIO server
  }

  getSocket() {
    return this.socket;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.on('connect', () => {
        console.log('Connected to WebSocket');
        resolve();
      });

      this.socket.on('error', (error: any) => {
        console.error('Error connecting to WebSocket:', error);
        reject(error);
      });
    });
  }

  subscribeWakeUpTopic(callback: (message: any) => void): void {
    this.socket.on('wake_up', (message: any) => {
      console.log('Received message:', message);
      callback(message);
    });
  }


  subscribeClockTopic(callback: (message: any) => void) {
    return this.socket.on('time', (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeAlarmTopic(callback: (message: any) => void) {
    return this.socket.on("ALARM", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribePeopleCountTopic(callback: (message: any) => void) {
    return this.socket.on("people_count", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeliveTemperatureTopic(callback: (message: any) => void) {
    return this.socket.on("api_temp", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeliveInsideTemperatureTopic(callback: (message: any) => void) {
    return this.socket.on("api_temp_inside", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribSystemStateTopic(callback: (message: any) => void) {
    return this.socket.on("system_state", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeToWindowTopic(callback: (message: any) => void) {
    return this.socket.on("windows", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeToProcenatTopic(callback: (message: any) => void) {
    return this.socket.on("pid_procenat", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeToPIDTopic(callback: (message: any) => void) {
    return this.socket.on("pid_data", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  subscribeToTypeStateTopic(callback: (message: any) => void) {
    return this.socket.on("type_state", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }


  subscribeToActualFanSpeedTopic(callback: (message: any) => void) {
    return this.socket.on("fanspeed_display", (message: any) => {
      console.log('Received message:', message);
      callback(JSON.parse(message));
    });
  }

  disconnect(): void {
    if (this.socket && this.socket.connected) {
      this.socket.disconnect();
    }
  }
}
