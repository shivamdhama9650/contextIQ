export default function AdminLoading() {
  return <OperationalLoading title="Admin console" />;
}

function OperationalLoading({ title }: { title: string }) {
  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-6xl">
        <div className="border-b border-slate-200 pb-6">
          <div className="h-4 w-32 rounded bg-blue-100" />
          <div className="mt-3 h-9 w-64 rounded bg-slate-200" />
          <p className="sr-only">Loading {title}</p>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {[0, 1, 2].map((item) => (
            <div className="h-28 rounded-lg border border-slate-200 bg-white" key={item} />
          ))}
        </div>
        <div className="mt-8 h-72 rounded-lg border border-slate-200 bg-white" />
      </section>
    </main>
  );
}
