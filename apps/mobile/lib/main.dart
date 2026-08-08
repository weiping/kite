import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

import 'capture/audio_recorder.dart';
import 'capture/classify.dart';
import 'capture/search.dart';
import 'capture/voice_entry.dart';
import 'capture/whisper_transcriber.dart';
import 'store/store.dart';

void main() => runApp(const KiteApp());

class KiteApp extends StatelessWidget {
  const KiteApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Kite',
        theme: ThemeData(colorSchemeSeed: const Color(0xFF3B82F6), useMaterial3: true),
        home: const HomeScreen(),
      );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final ItemStore _store;
  final VoiceRecorder _recorder = VoiceRecorder();
  final WhisperTranscriber _transcriber = WhisperTranscriber();
  final VoiceEntry _entry = VoiceEntry();
  final _inputCtl = TextEditingController();
  final _queryCtl = TextEditingController();
  List<Item> _items = [];
  String _status = '初始化…';

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    final dir = await getApplicationDocumentsDirectory();
    _store = ItemStore('${dir.path}/items.json');
    await _refresh();
    final modelDir = '${dir.path}/whisper-small';
    if (await File('$modelDir/encoder.int8.onnx').exists()) {
      try {
        _transcriber.init(modelDir);
        if (mounted) setState(() => _status = '长按麦克风说话，或下方输入文本');
      } catch (e) {
        if (mounted) setState(() => _status = 'whisper init 失败: $e');
      }
    } else if (mounted) {
      setState(() => _status = '下方输入文本（whisper 模型未装，录音转写不可用）');
    }
  }

  Future<void> _refresh() async {
    final items = await _store.list();
    if (mounted) setState(() => _items = items);
  }

  Future<void> _classifyAndStore(String text) async {
    for (final item in classify(text)) {
      await _store.add(item);
    }
    await _refresh();
  }

  Future<void> _onRecordStart() async {
    _entry.onStart();
    await _recorder.start();
    if (mounted) setState(() {});
  }

  Future<void> _onRecordSubmit() async {
    final path = await _recorder.stop();
    _entry.onSubmit();
    if (path != null && _transcriber.isReady) {
      final text = _transcriber.transcribe(path);
      if (text != null && text.isNotEmpty) await _classifyAndStore(text);
    }
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final recording = _entry.state == VoiceState.recording;
    final querying = _queryCtl.text.isNotEmpty;
    final result = querying ? search(_items, _queryCtl.text) : null;
    final shown = result != null ? result.matches.map((m) => m.item).toList() : _items;
    return Scaffold(
      appBar: AppBar(title: const Text('Kite 速记')),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: TextField(
            controller: _queryCtl,
            decoration: const InputDecoration(hintText: '搜索…', prefixIcon: Icon(Icons.search)),
            onChanged: (_) => setState(() {}),
          ),
        ),
        Text(_status, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        Expanded(
          child: ListView(
            children: shown.isEmpty
                ? const [Center(child: Padding(padding: EdgeInsets.all(40), child: Text('无内容')))]
                : [
                    for (final item in shown)
                      ListTile(
                        leading: Icon(item.kind == 'task'
                            ? Icons.check_circle_outline
                            : item.kind == 'event'
                                ? Icons.event
                                : Icons.note_outlined),
                        title: Text(item.title),
                        subtitle: Text(item.kind, style: const TextStyle(fontSize: 12)),
                      ),
                  ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
          child: Row(children: [
            Expanded(
              child: TextField(
                controller: _inputCtl,
                decoration: const InputDecoration(hintText: '输入文本，回车结构化'),
                onSubmitted: (text) async {
                  if (text.trim().isNotEmpty) {
                    await _classifyAndStore(text);
                    _inputCtl.clear();
                  }
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.send),
              onPressed: () async {
                final text = _inputCtl.text;
                if (text.trim().isNotEmpty) {
                  await _classifyAndStore(text);
                  _inputCtl.clear();
                }
              },
            ),
          ]),
        ),
      ]),
      floatingActionButton: recording || _transcriber.isReady
          ? Listener(
              onPointerDown: (_) => _onRecordStart(),
              onPointerUp: (_) => _onRecordSubmit(),
              child: Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: recording ? Colors.red : const Color(0xFF3B82F6),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.25),
                      blurRadius: 10,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Icon(recording ? Icons.stop : Icons.mic, color: Colors.white, size: 30),
              ),
            )
          : null,
    );
  }
}
