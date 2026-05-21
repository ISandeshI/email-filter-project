export default function DataTable({
  columns,
  data,
  renderRow
}) {
  return (

    <div className="
      bg-white
      rounded-xl
      shadow-sm
      overflow-hidden
    ">

      <div className="overflow-x-auto">

        <table className="
          w-full
          min-w-[900px]
          text-sm
          text-left
        ">

          {/* Header */}
          <thead className="
            bg-gray-100
            text-gray-600
            uppercase
            text-xs
          ">

            <tr>

              {columns.map((col, index) => (

                <th
                  key={index}
                  className="px-6 py-3"
                >
                  {col.label}
                </th>

              ))}

            </tr>

          </thead>

          {/* Body */}
          <tbody className="divide-y divide-gray-100">

            {data.map((item, index) =>
              renderRow(item, index)
            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}