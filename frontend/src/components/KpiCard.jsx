export default function KpiCard({
  title,
  value
}) {
  return (
    <div className="
      bg-white
      p-5
      rounded-xl
      border
      border-gray-200
      shadow-sm
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

    </div>
  );
}