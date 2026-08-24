import { ChangeDetectionStrategy, Component, inject, computed } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ThemeService } from '../../../core/services';
import { ThemeMode } from '../../../core/models';

@Component({
  selector: 'app-theme-toggle',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MatButtonModule, MatIconModule, MatMenuModule, MatTooltipModule],
  templateUrl: './theme-toggle.component.html',
  styleUrl: './theme-toggle.component.scss',
})
export class ThemeToggleComponent {
  private readonly themeService = inject(ThemeService);

  protected readonly ThemeMode = ThemeMode;
  protected readonly currentTheme = this.themeService.themeMode;

  protected readonly currentIcon = computed(() => {
    switch (this.currentTheme()) {
      case ThemeMode.LIGHT:
        return 'light_mode';
      case ThemeMode.DARK:
        return 'dark_mode';
      case ThemeMode.SYSTEM:
        return 'computer';
      default:
        return 'brightness_auto';
    }
  });

  protected selectTheme(theme: ThemeMode): void {
    this.themeService.setTheme(theme);
  }
}
