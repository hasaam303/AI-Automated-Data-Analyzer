import ChartCard from "./ChartCard";

export default function ChartGrid({ charts, title = "Visualizations" }) {
  if (!charts || charts.length === 0) return null;

  return (
    <div>
      <h2 className="section-title">{title}</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {charts.map((chart) => (
          <ChartCard key={chart.id} chart={chart} />
        ))}
      </div>
    </div>
  );
}
