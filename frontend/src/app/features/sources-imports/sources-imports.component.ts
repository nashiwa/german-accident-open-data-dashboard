import { AsyncPipe, DatePipe, NgFor, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';

import { ApiService } from '../../core/api.service';

@Component({
  selector: 'app-sources-imports',
  standalone: true,
  imports: [AsyncPipe, DatePipe, NgFor, NgIf],
  templateUrl: './sources-imports.component.html',
  styleUrl: './sources-imports.component.scss',
})
export class SourcesImportsComponent {
  private readonly api = inject(ApiService);
  readonly sources$ = this.api.getSources();
  readonly importRuns$ = this.api.getImportRuns();
}
