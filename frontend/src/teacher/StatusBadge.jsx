const LABELS = {
  uploaded: { icon: "○", text: "Uploaded" },
  processing: { icon: "…", text: "Processing" },
  ready: { icon: "✓", text: "Ready" },
  failed: { icon: "!", text: "Needs re-upload" },
};

export default function StatusBadge({ status }) {
  const s = LABELS[status] ?? LABELS.uploaded;
  return (
    <span className={`status ${status}`}>
      <span aria-hidden="true">{s.icon}</span>
      {s.text}
    </span>
  );
}
