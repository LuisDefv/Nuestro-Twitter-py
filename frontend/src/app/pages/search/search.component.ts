import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './search.component.html',
  styleUrl: './search.component.scss',
})
export class SearchComponent {
  private http = inject(HttpClient);

  private readonly apiBase = environment.apiUrl;

  query = '';
  results = signal<any[]>([]);
  searching = signal(false);
  searched = signal(false);

  search(): void {
    if (!this.query.trim()) return;
    this.searching.set(true);
    this.searched.set(true);
    this.http.get<any>(`${this.apiBase}/users/?q=${encodeURIComponent(this.query)}`).subscribe({
      next: (res) => {
        this.results.set(res.results || res);
        this.searching.set(false);
      },
      error: () => this.searching.set(false),
    });
  }
}
