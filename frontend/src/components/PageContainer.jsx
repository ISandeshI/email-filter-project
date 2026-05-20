export default function PageContainer({ title, children, actions }) {
  return (
    <div className="p-6 bg-gray-50 min-h-screen space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-800">
          {title}
        </h2>

        {actions && (
          <div className="flex items-center gap-3">
            {actions}
          </div>
        )}
      </div>

      {/* Content */}
      <div>{children}</div>
    </div>
  );
}