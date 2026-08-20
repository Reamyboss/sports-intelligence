/**
 * Competition names come from football-data.org. A few differ from
 * what people actually call them - most notably La Liga, filed as
 * "Primera Division", which makes a fully populated competition look
 * absent to anyone scanning for the familiar name.
 *
 * Display only. The API name stays the key everywhere else, so
 * filtering and lookups are unaffected.
 */
const DISPLAY_NAMES: Record<string, string> = {
  'Primera Division': 'La Liga',
  'Campeonato Brasileiro Série A': 'Brasileirão',
}

export function competitionLabel(name: string): string {
  return DISPLAY_NAMES[name] ?? name
}
