import { DecimalPipe, NgFor, NgIf } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { timeout } from 'rxjs';

import { AccidentPointRecord, ApiService } from '../../core/api.service';

interface MapPoint {
  id: string;
  x: number;
  y: number;
  label: string;
}

@Component({
  selector: 'app-map-view',
  standalone: true,
  imports: [DecimalPipe, FormsModule, NgFor, NgIf],
  templateUrl: './map-view.component.html',
  styleUrl: './map-view.component.scss',
})
export class MapViewComponent implements OnInit {
  year = 2023;
  state = 'SH';
  participant = '';
  accidents: AccidentPointRecord[] = [];
  points: MapPoint[] = [];
  status = 'Loading preview points...';

  constructor(private readonly api: ApiService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.status = 'Loading preview points...';
    this.api.getAccidentPoints({ year: this.year, state: this.state, participant: this.participant }).pipe(timeout(4000)).subscribe({
      next: (response) => {
        this.accidents = response.results;
        this.points = this.toPoints(response.results);
        this.status = response.results.length ? '' : 'No preview rows matched these filters.';
      },
      error: (error) => {
        this.accidents = [];
        this.points = [];
        this.status = `Could not load preview rows: ${error.status || error.name || 'network error'}`;
      },
    });
  }

  private toPoints(accidents: AccidentPointRecord[]): MapPoint[] {
    const coordinates = accidents
      .map((accident) => ({
        accident,
        longitude: accident.longitude,
        latitude: accident.latitude,
      }))
      .filter((item) => Number.isFinite(item.longitude) && Number.isFinite(item.latitude));

    if (coordinates.length === 0) {
      return [];
    }

    const longitudes = coordinates.map((item) => item.longitude);
    const latitudes = coordinates.map((item) => item.latitude);
    const minLongitude = Math.min(...longitudes);
    const maxLongitude = Math.max(...longitudes);
    const minLatitude = Math.min(...latitudes);
    const maxLatitude = Math.max(...latitudes);
    const longitudeRange = maxLongitude - minLongitude || 1;
    const latitudeRange = maxLatitude - minLatitude || 1;

    return coordinates.map(({ accident, longitude, latitude }) => ({
      id: accident.id,
      x: 32 + ((longitude - minLongitude) / longitudeRange) * 536,
      y: 32 + ((maxLatitude - latitude) / latitudeRange) * 296,
      label: accident.participant,
    }));
  }
}
