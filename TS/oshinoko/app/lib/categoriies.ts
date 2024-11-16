export interface CategoryItem {
  id: string;
  name: string;
  image: string;
}

export const categories: CategoryItem[] = [
  { id: 'aespa', name: 'Aespa', image: '/whisplash.png' },
  { id: 'takarazuka', name: '宝塚', image: '/takarazuka_kageki.png' },
  { id: 'bts', name: 'BTS', image: '/BTS.jpeg' },
  { id: 'illit', name: 'ILLIT', image: '/illit.jpeg' },
  // Add more categories as needed
  // ロゴは, TS/oshinoko/public に入っている.
];
