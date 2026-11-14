// Times are seconds relative to the caption card, not editing-API microseconds.
// Apply only to selected semantic keywords. This helper never changes color.
export function keywordScale({time, start, captionEnd, peakScale = 1.2, duration = 0.28}) {
  if (![time, start, captionEnd, peakScale, duration].every(Number.isFinite)) return 1;
  const span = Math.min(Math.max(0, duration), captionEnd - start);
  if (span < 0.06 || time < start || time >= start + span) return 1;
  const t = (time - start) / span;
  const peak = Math.min(1.25, Math.max(1, peakScale));
  const smooth = x => x * x * (3 - 2 * x);
  const amount = t < 0.28 ? smooth(t / 0.28)
    : t <= 0.43 ? 1 : 1 - smooth((t - 0.43) / 0.57);
  return 1 + (peak - 1) * amount;
}
