import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, LoginComponent, HomeComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'Rasmi';
  isLoggedIn: boolean = false;

  constructor() {
    // Check if previously logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    if (isLoggedIn === 'true') {
      this.isLoggedIn = true;
    }
  }

  onLoginSuccess() {
    this.isLoggedIn = true;
    localStorage.setItem('isLoggedIn', 'true');
  }

  onLogout() {
    this.isLoggedIn = false;
    localStorage.removeItem('isLoggedIn');
  }
}
