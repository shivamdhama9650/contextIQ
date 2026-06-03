export default function DashboardLoading() {
  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-6xl">
        <div className="border-b border-slate-200 pb-6">
          <div className="h-4 w-52 rounded bg-blue-100" />
          <div className="mt-3 h-9 w-72 rounded bg-slate-200" />
          <div className="mt-4 h-4 w-full max-w-2xl rounded bg-slate-100" />
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {[0, 1, 2].map((item) => (
            <div className="h-28 rounded-lg border border-slate-200 bg-white" key={item} />
          ))}
        </div>
        <div className="mt-8 grid gap-4 lg:grid-cols-4">
          {[0, 1, 2, 3].map((item) => (
            <div className="h-44 rounded-lg border border-slate-200 bg-white" key={item} />
          ))}
        </div>
      </section>
    </main>
  );
}
