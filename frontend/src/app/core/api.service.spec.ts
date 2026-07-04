import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('requests mandatory questions', () => {
    service.getMandatoryQuestions().subscribe();

    const request = http.expectOne('http://127.0.0.1:8000/api/questions/mandatory/');
    expect(request.request.method).toBe('GET');
    request.flush({ questions: {}, provenance: [] });
  });

  it('serializes aggregate filters', () => {
    service.getAccidentAggregate({ year: 2023, state: 'SH', participant: '' }).subscribe();

    const request = http.expectOne('http://127.0.0.1:8000/api/aggregates/accidents/?year=2023&state=SH');
    expect(request.request.method).toBe('GET');
    request.flush({ accident_count: 0, filters: {}, provenance: [] });
  });

  it('requests zero-accident municipalities with required filters', () => {
    service.getZeroAccidentMunicipalities({ year: 2023, state: 'SH' }).subscribe();

    const request = http.expectOne('http://127.0.0.1:8000/api/bonus/zero-accident-municipalities/?year=2023&state=SH');
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });

  it('requests lightweight accident points for the map preview', () => {
    service.getAccidentPoints({ year: 2023, state: 'SH' }).subscribe();

    const request = http.expectOne('http://127.0.0.1:8000/api/bonus/accident-points/?year=2023&state=SH');
    expect(request.request.method).toBe('GET');
    request.flush({ results: [], filters: {} });
  });
});
