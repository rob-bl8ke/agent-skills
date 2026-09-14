/**
 * Available brand color palettes
 */
export enum Palette {
  BLUE = 'blue',
  GREEN = 'green',
  TEAL = 'teal',
  PURPLE = 'purple',
  PINK = 'pink',
  GOLD = 'gold',
  RED = 'red',
}

/**
 * Palette metadata for UI display
 */
export interface PaletteInfo {
  id: Palette;
  name: string;
  color: string; // Primary color for swatch display
}

/**
 * All available palettes with display info
 */
export const PALETTES: PaletteInfo[] = [
  { id: Palette.BLUE, name: 'Blue', color: '#3b82f6' },
  { id: Palette.GREEN, name: 'Green', color: '#22c55e' },
  { id: Palette.TEAL, name: 'Teal', color: '#14b8a6' },
  { id: Palette.PURPLE, name: 'Purple', color: '#a855f7' },
  { id: Palette.PINK, name: 'Pink', color: '#ec4899' },
  { id: Palette.GOLD, name: 'Gold', color: '#eab308' },
  { id: Palette.RED, name: 'Red', color: '#ef4444' },
];
