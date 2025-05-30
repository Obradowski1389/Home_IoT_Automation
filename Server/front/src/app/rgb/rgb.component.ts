import { Component } from '@angular/core';
import { ServiceService } from '../service/service.service';

@Component({
  selector: 'app-rgb',
  templateUrl: './rgb.component.html',
  styleUrls: ['./rgb.component.css']
})
export class RgbComponent {
  colors = [
    {color: "#FF0000", number: "1"},
    {color: "#00CC00", number: "2"},
    {color: "#0000FF", number: "3"},
    {color: "#FFFF00", number: "4"},
    {color: "#800080", number: "5"},
    {color: "#87CEFA", number: "6"},
    {color: "#FFFAFA", number: "7"}
  ] 
  // colors: string[] = ["#FF0000", "#00CC00", "#0000FF", "#FFFF00", "#800080", "#87CEFA", "#FFFAFA"];
  selectedColor: string | null = null;


  constructor(private service: ServiceService) { }

  ngOnInit(): void {
    // TODO: Get current color
  }

  getChunkedColors(): { color: string, number: string }[][] {
    const chunkSize = 3;
    const chunkedColors: { color: string, number: string }[][] = [];
  
    for (let i = 0; i < this.colors.length; i += chunkSize) {
      chunkedColors.push(this.colors.slice(i, i + chunkSize));
    }
  
    return chunkedColors;
  }

  isColorSelected(color: string): boolean {
    return this.selectedColor === color;
  }

  selectColor(color: any){
    this.selectedColor = color.color;
    console.log(color);

    this.service.change_rgb_color(color.number).subscribe((data: any) => {
      console.log(data);
    });
  }

  turnOff(){
    this.selectedColor = null;
    this.service.change_rgb_color("OK").subscribe((data: any) => {
      console.log(data);
    });
  }

}
