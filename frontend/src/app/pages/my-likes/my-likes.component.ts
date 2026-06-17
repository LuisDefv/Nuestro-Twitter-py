import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';
import { FormatContentPipe } from '../../shared/format-content.pipe';
import { Post } from '../../shared/post.types';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-my-likes',
  standalone: true,
  imports: [DatePipe, RouterLink, FormatContentPipe],
  template: `
    <section class="my-likes">
      <header>
        <h1>&gt; mis_likes</h1>
      </header>

      @if (loading()) {
        <article class="card card--loading"><p>&gt; cargando...</p></article>
      } @else {
        @for (post of posts(); track post.id) {
          <article class="card post">
            <header class="post__head">
              <div class="post__author-wrap">
                <a class="post__avatar-link" [routerLink]="['/users', post.author_username]">
                  @if (post.author_avatar) {
                    <img class="post__avatar" [src]="post.author_avatar" alt="" />
                  } @else {
                    <div class="post__avatar post__avatar--placeholder">{{ post.author_username[0] }}</div>
                  }
                </a>
                <div class="post__author-meta">
                  <a class="post__author" [routerLink]="['/users', post.author_username]">&#64;{{ post.author_username }}</a>
                  <time class="post__date">{{ post.created_at | date:'short' }}</time>
                </div>
              </div>
            </header>
            @if (post.image_url) {
              <img class="post__img" [src]="post.image_url" alt="" />
            }
            <p class="post__body" [innerHTML]="post.content | formatContent"></p>
            <footer class="post__foot">
              <button class="action-btn" [routerLink]="['/post', post.id]" title="Comentar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                {{ post.reply_count }}
              </button>
              <button class="action-btn like-btn liked" (click)="toggleLike(post)" title="Me gusta">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
                {{ post.likes_count }}
              </button>
            </footer>
          </article>
        } @empty {
          <article class="card"><p>&gt; sin likes todavía.</p></article>
        }
      }
    </section>
  `,
  styles: [`
    :host { display: block; max-width: 760px; margin: 0 auto; padding: 1.5rem 1rem 5rem; }
    .my-likes header { margin-bottom: 1.5rem; }
    .my-likes h1 { color: var(--neon); font-size: 1.2rem; text-shadow: 0 0 6px var(--neon); }
    .card {
      background: var(--bg-soft); border: 1px solid var(--border); border-radius: 4px;
      padding: 1rem 1.25rem; margin-bottom: 0.9rem;
      box-shadow: 0 0 0 1px var(--neon-tint), 0 0 12px var(--neon-tint);
    }
    .card--loading { color: var(--muted); }
    .post__head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
    .post__author-wrap { display: flex; align-items: center; gap: 0.6rem; }
    .post__author-meta { display: flex; flex-direction: column; gap: 0.1rem; }
    .post__avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
    .post__avatar--placeholder { background: var(--neon); color: var(--bg); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; }
    .post__avatar-link { display: flex; text-decoration: none; }
    .post__author { color: var(--neon); font-weight: 700; text-shadow: 0 0 4px var(--neon-glow); text-decoration: none; }
    .post__date { color: var(--muted); font-size: 0.78rem; }
    .post__img { max-width: 100%; max-height: 400px; border-radius: 4px; margin-bottom: 0.5rem; object-fit: cover; }
    .post__body { margin: 0.25rem 0 0.75rem; line-height: 1.5; color: var(--text); white-space: pre-wrap; }
    .post__foot { display: flex; gap: 0.5rem; color: var(--neon-dim); font-size: 0.82rem; border-top: 1px dashed var(--border); padding-top: 0.5rem; margin-top: 0.5rem; }
    .action-btn { background: none; border: none; color: var(--muted); cursor: pointer; font-family: inherit; display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.82rem; padding: 0.25rem 0.4rem; border-radius: 4px; transition: color 0.15s; text-decoration: none; }
    .action-btn:hover { color: var(--neon); }
    .like-btn.liked { color: #ff4081; svg { fill: #ff4081; } }
    .like-btn:hover { color: #ff4081; }
  `]
})
export class MyLikesComponent implements OnInit {
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private readonly apiBase = environment.apiUrl;

  posts = signal<Post[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    const username = this.auth.username();
    if (!username) return;
    this.http.get<any>(`${this.apiBase}/users/${username}/posts/?tab=likes`).subscribe({
      next: (res) => this.posts.set(res.results || []),
      error: () => {},
      complete: () => this.loading.set(false),
    });
  }

  toggleLike(post: Post): void {
    this.http.request('DELETE', `${this.apiBase}/posts/${post.id}/like/`, { responseType: 'text' }).subscribe({
      next: () => {
        this.posts.update(list => list.filter(p => p.id !== post.id));
      },
    });
  }
}
