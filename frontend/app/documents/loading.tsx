export default function DocumentsLoading() {
  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-5xl">
        <div className="border-b border-slate-200 pb-6">
          <div className="h-4 w-44 rounded bg-blue-100" />
          <div className="mt-3 h-9 w-56 rounded bg-slate-200" />
          <div className="mt-4 h-4 w-full max-w-xl rounded bg-slate-100" />
        </div>
        <div className="mt-8 rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          <div className="h-4 w-40 rounded bg-slate-200" />
          <div className="mt-6 space-y-3">
            {[0, 1, 2].map((item) => (
              <div className="h-12 rounded-md bg-slate-100" key={item} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
