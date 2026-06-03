export default function DocumentDetailLoading() {
  return (
    <main className="min-h-screen bg-surface px-6 py-10 text-ink">
      <section className="mx-auto max-w-4xl">
        <div className="h-5 w-36 rounded bg-slate-200" />
        <div className="mt-8 h-4 w-40 rounded bg-slate-200" />
        <div className="mt-3 h-10 w-2/3 rounded bg-slate-200" />
        <div className="mt-4 flex gap-3">
          <div className="h-8 w-20 rounded-full bg-slate-200" />
          <div className="h-8 w-24 rounded-full bg-slate-200" />
          <div className="h-8 w-28 rounded-full bg-slate-200" />
        </div>
        <div className="mt-8 space-y-4">
          <div className="h-44 rounded-lg border border-slate-200 bg-white shadow-sm" />
          <div className="h-44 rounded-lg border border-slate-200 bg-white shadow-sm" />
        </div>
      </section>
    </main>
  );
}
