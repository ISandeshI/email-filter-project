import Card from "./Card";

export default function KpiCard({
  title,
  value
}) {
  return (

    <Card className="
      border
      border-gray-100
    ">

      <p className="
        text-sm
        text-gray-500
        mb-2
      ">
        {title}
      </p>

      <p className="
        text-3xl
        font-bold
        text-gray-800
      ">
        {value}
      </p>

    </Card>
  );
}