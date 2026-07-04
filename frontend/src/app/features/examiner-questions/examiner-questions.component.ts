import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';

import { ApiService, MandatoryQuestionsResponse, QuestionEntry } from '../../core/api.service';

interface QuestionCard {
  key: string;
  label: string;
  value: string;
  endpoint: string;
}

@Component({
  selector: 'app-examiner-questions',
  standalone: true,
  imports: [AsyncPipe, NgFor, NgIf],
  templateUrl: './examiner-questions.component.html',
  styleUrl: './examiner-questions.component.scss',
})
export class ExaminerQuestionsComponent {
  private readonly api = inject(ApiService);
  readonly result$ = this.api.getMandatoryQuestions();

  cards(result: MandatoryQuestionsResponse): QuestionCard[] {
    return [
      this.card('earliest_accident_year', 'Earliest accident year', result.questions['earliest_accident_year'], 'earliest_year'),
      this.card('saxony_accidents_2023', 'Saxony accidents in 2023', result.questions['saxony_accidents_2023'], 'accident_count'),
      this.card('nrw_earliest_year', 'NRW data available from', result.questions['nrw_earliest_year'], 'earliest_year'),
      this.card(
        'mecklenburg_vorpommern_earliest_year',
        'Mecklenburg-Western Pomerania from',
        result.questions['mecklenburg_vorpommern_earliest_year'],
        'earliest_year',
      ),
      this.card(
        'berlin_pedestrian_accidents_2023',
        'Berlin pedestrian accidents in 2023',
        result.questions['berlin_pedestrian_accidents_2023'],
        'accident_count',
      ),
    ];
  }

  private card(key: string, label: string, entry: QuestionEntry | undefined, answerKey: string): QuestionCard {
    const rawValue = entry?.answer?.[answerKey];
    return {
      key,
      label,
      value: rawValue === null || rawValue === undefined ? 'No data yet' : String(rawValue),
      endpoint: entry?.endpoint ?? '',
    };
  }
}
