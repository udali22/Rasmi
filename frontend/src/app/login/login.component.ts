
import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';


@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss']
})
export class LoginComponent {
    @Output() loginSuccess = new EventEmitter<void>();

    onLogin() {
        this.loginSuccess.emit();
    }
}
