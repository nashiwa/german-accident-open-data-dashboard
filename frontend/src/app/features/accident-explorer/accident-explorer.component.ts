import { AsyncPipe, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';

import { AccidentAggregateResponse, ApiService } from '../../core/api.service';

@Component({
  selector: 'app-accident-explorer',
  standalone: true,
  imports: [FormsModule, AsyncPipe, NgIf],
  templateUrl: './accident-explorer.component.html',
  styleUrl: './accident-explorer.component.scss',
})
export class AccidentExplorerComponent {
  year = 2023;
  state = 'SH';
  participant = '';
  result$?: Observable<AccidentAggregateResponse>;

  constructor(private readonly api: ApiService) {}

  search() {
    this.result$ = this.api.getAccidentAggregate({
      year: this.year,
      state: this.state,
      participant: this.participant,
    });
  }
}
