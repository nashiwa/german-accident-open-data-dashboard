import { DecimalPipe, NgFor, NgIf } from '@angular/common';
import { Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Chart, registerables } from 'chart.js';

import { ApiService, RateAggregateResponse, RateRankingRow } from '../../core/api.service';

Chart.register(...registerables);

@Component({
  selector: 'app-rates-rankings',
  standalone: true,
  imports: [FormsModule, DecimalPipe, NgFor, NgIf],
  templateUrl: './rates-rankings.component.html',
  styleUrl: './rates-rankings.component.scss',
})
export class RatesRankingsComponent {
  @ViewChild('rankingChart') private readonly rankingChart?: ElementRef<HTMLCanvasElement>;

  year = 2023;
  level = 'district';
  result?: RateAggregateResponse;
  private chart?: Chart;

  constructor(private readonly api: ApiService) {}

  ngOnDestroy() {
    this.chart?.destroy();
  }

  load() {
    this.api.getRates({ year: this.year, level: this.level }).subscribe((result) => {
      this.result = result;
      setTimeout(() => this.renderChart(result.results));
    });
  }

  private renderChart(rows: RateRankingRow[]) {
    this.chart?.destroy();
    const canvas = this.rankingChart?.nativeElement;
    if (!canvas || rows.length === 0) {
      return;
    }
    const topRows = rows.slice(0, 10);
    this.chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: topRows.map((row) => row.name || row.ags),
        datasets: [
          {
            label: 'Accidents per 100,000 residents',
            data: topRows.map((row) => row.rate_per_100000),
            backgroundColor: '#0f4c81',
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `${Number(context.parsed.y ?? 0).toFixed(1)} per 100,000`,
            },
          },
        },
        scales: {
          x: { ticks: { maxRotation: 35, minRotation: 0 } },
          y: { beginAtZero: true },
        },
      },
    });
  }
}
