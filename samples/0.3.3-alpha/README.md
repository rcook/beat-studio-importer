# Sample patterns from Beat Studio 0.3.3-ALPHA

Since these patterns are included in this version of Beat Studio by default, importing any
of them with the same name as the original pattern should be a no-op. For example:

```bash
python \
    ./beat-studio-importer.py \
    import \
    samples/0.3.3-alpha/Demo_Basic_Rock.mid \
    --name 'Demo - Basic Rock' \
    --add
```

This should report _An identical pattern Demo - Basic Rock is already defined in C:\path\to\Beat Studio\patterns.beat_.

* [`Demo_Basic_Rock.mid`](Demo_Basic_Rock.mid)
  * "Demo - Basic Rock"
  * 32 beats, 120 BPM
  * Note length: Sixteenth notes
  * Time signature: 4/4
  * 24 drum notes
* [`Demo_Just_hihat.mid`](Demo_Just_hihat.mid)
  * "Demo - Just hihat"
  * 32 beats, 120 BPM
  * Note length: Sixteenth notes
  * Time signature: 4/4
  * 18 drum notes
* [`Demo_Easy_beat.mid`](Demo_Easy_beat.mid)
  * "Demo - Easy beat"
  * 64 beats, 120 BPM
  * Note length: Sixteenth notes
  * Time signature: 4/4
  * 54 drum notes
* [`Demo_Fill.mid`](Demo_Fill.mid)
  * "Demo - Fill"
  * 32 beats, 110 BPM
  * Note length: Sixteenth notes
  * Time signature: 4/4
  * 25 drum notes
* [`Demo_Groove.mid`](Demo_Groove.mid)
  * "Demo - Groove"
  * 32 beats, 95 BPM
  * Note length: Sixteenth notes
  * Time signature: 4/4
  * 38 drum notes
