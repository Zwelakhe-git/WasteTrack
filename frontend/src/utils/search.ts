// Поиск продуктов в терминале.
// Регистр и «ё/е» не важны; запрос делится на слова, и каждое слово должно
// встречаться в названии или категории: «кот вопп» найдёт «Котлета для Воппера».

export const normalize = (text: string): string =>
  text.toLowerCase().replace(/ё/g, 'е').trim();

export function matchesQuery(query: string, ...fields: (string | undefined)[]): boolean {
  const words = normalize(query).split(/\s+/).filter(Boolean);
  if (words.length === 0) return true;
  const haystack = normalize(fields.filter(Boolean).join(' '));
  return words.every(word => haystack.includes(word));
}
