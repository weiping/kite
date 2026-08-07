// 端侧本地检索（Dart，n-gram）。复刻 services/capture/search.py；契约 task-ret-search。
// 来源 = 匹配的 item 本身；无匹配 found=false（不编造，charter 第4条）。
import 'classify.dart';

class Match {
  final Item item;
  final int score;
  const Match(this.item, this.score);
}

class SearchResult {
  final List<Match> matches;
  const SearchResult(this.matches);
  bool get found => matches.isNotEmpty;
}

List<String> _tokens(String query) {
  final q = query.trim();
  final bigrams = [for (int i = 0; i < q.length - 1; i++) q.substring(i, i + 2)];
  final chars = q.split('').where((c) => c.trim().isNotEmpty).toList();
  return [...bigrams, ...chars].where((t) => t.trim().isNotEmpty).toList();
}

SearchResult search(List<Item> items, String query) {
  final tokens = _tokens(query).toSet();
  final matches = <Match>[];
  for (final item in items) {
    final score = tokens.where((t) => item.title.contains(t) || item.text.contains(t)).length;
    if (score > 0) matches.add(Match(item, score));
  }
  matches.sort((a, b) => b.score.compareTo(a.score));
  return SearchResult(matches);
}
