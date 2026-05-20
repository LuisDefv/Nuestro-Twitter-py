import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { NotificationService } from '../core/notification.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss',
})
export class LayoutComponent implements OnInit {
  private auth = inject(AuthService);
  private router = inject(Router);
  private notif = inject(NotificationService);

  username = this.auth.username;
  menuOpen = signal(false);
  unreadCount = this.notif.unreadCount;

  ngOnInit(): void {
    this.notif.fetchUnreadCount();
    setInterval(() => this.notif.fetchUnreadCount(), 30000);
  }

  toggleMenu(): void {
    this.menuOpen.update((v) => !v);
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
