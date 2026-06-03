export default function AnalyticsLoading() {
  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-6xl">
        <div className="border-b border-slate-200 pb-6">
          <div className="h-4 w-40 rounded bg-blue-100" />
          <div className="mt-3 h-9 w-72 rounded bg-slate-200" />
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[0, 1, 2, 3].map((item) => (
            <div className="h-28 rounded-lg border border-slate-200 bg-white" key={item} />
          ))}
        </div>
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="h-72 rounded-lg border border-slate-200 bg-white" />
          <div className="h-72 rounded-lg border border-slate-200 bg-white" />
        </div>
      </section>
    </main>
  );
}
