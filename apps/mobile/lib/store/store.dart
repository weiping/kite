// 端侧本地存储（Dart，JSON 文件 + path_provider）。
// 复刻 services/store/store.py；契约 task-store。离线、可导出。
import 'dart:convert';
import 'dart:io';

import 'package:kite_mobile/capture/classify.dart';

class ItemStore {
  final String path;
  ItemStore(this.path);

  Future<void> add(Item item) async {
    final items = await list();
    items.add(item);
    await _save(items);
  }

  Future<List<Item>> list() async {
    final f = File(path);
    if (!await f.exists()) return [];
    try {
      final raw = jsonDecode(await f.readAsString()) as List;
      return raw.map((d) => Item.fromJson(d as Map<String, dynamic>)).toList();
    } catch (_) {
      return []; // 文件损坏兜底：读空
    }
  }

  Future<void> clear() async => _save([]);

  Future<void> _save(List<Item> items) async {
    final f = File(path);
    await f.parent.create(recursive: true);
    await f.writeAsString(
      const JsonEncoder.withIndent('  ').convert(items.map((i) => i.toJson()).toList()),
    );
  }
}
