import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DhtComponent } from './dht.component';

describe('DhtComponent', () => {
  let component: DhtComponent;
  let fixture: ComponentFixture<DhtComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DhtComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DhtComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
