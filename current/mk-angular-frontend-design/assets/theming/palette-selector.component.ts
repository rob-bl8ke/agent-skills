import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PaletteService } from '../../../core/services';
import { Palette, PaletteInfo } from '../../../core/models';

@Component({
  selector: 'app-palette-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MatButtonModule, MatIconModule, MatMenuModule, MatTooltipModule],
  templateUrl: './palette-selector.component.html',
  styleUrl: './palette-selector.component.scss',
})
export class PaletteSelectorComponent {
  private readonly paletteService = inject(PaletteService);

  protected readonly palettes = this.paletteService.palettes;
  protected readonly currentPalette = this.paletteService.palette;

  protected selectPalette(palette: Palette): void {
    this.paletteService.setPalette(palette);
  }

  protected isSelected(palette: PaletteInfo): boolean {
    return this.currentPalette() === palette.id;
  }
}
