import { useEffect, useState } from "react";
import {
  loadKPIs, loadWeekly, loadQuarterly, loadMonthly, loadActivities,
  loadWeeklyPlan, loadCoaches, fmtDate,
} from "./data/loaders.js";
import Hero from "./components/Hero.jsx";
import RecentActivities from "./components/RecentActivities.jsx";
import RunningSection from "./components/RunningSection.jsx";
import StrengthSection from "./components/StrengthSection.jsx";
import HistorySection from "./components/HistorySection.jsx";
import CoachProfiles from "./components/CoachProfiles.jsx";
import WeeklyPlan from "./components/WeeklyPlan.jsx";

export default function App() {
  const [tab, setTab] = useState("jornada");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([loadKPIs(), loadWeekly(), loadQuarterly(), loadMonthly(), loadActivities()])
      .then(async ([kpis, weekly, quarterly, monthly, activities]) => {
        // weekly_plan.json e coaches.json são opcionais
        const plan = await loadWeeklyPlan().catch(() => null);
        const coaches = await loadCoaches().catch(() => null);
        setData({
          kpis, weekly: weekly.weeks, quarterly: quarterly.quarters,
          monthly: monthly.months, activities: activities.activities, plan, coaches,
        });
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error">Erro ao carregar os dados: {error}</div>;
  if (!data) return <div className="loading">Carregando dados do Strava…</div>;

  const openPlan = () => {
    setTab("plano");
    window.scrollTo({ top: 0 });
  };

  return (
    <>
      <nav className="nav">
        <div className="nav-inner">
          <div className="brand"><span className="brand-mark" aria-hidden="true" />RunForrestRun</div>
          <div className="tabs" role="tablist" aria-label="Seções">
            <button
              role="tab" id="tab-jornada" aria-selected={tab === "jornada"} aria-controls="panel"
              className={`tab ${tab === "jornada" ? "active" : ""}`} onClick={() => setTab("jornada")}
            >
              Jornada
            </button>
            <button
              role="tab" id="tab-plano" aria-selected={tab === "plano"} aria-controls="panel"
              className={`tab ${tab === "plano" ? "active" : ""}`} onClick={() => setTab("plano")}
            >
              <span className="tab-long">Plano semanal</span>
              <span className="tab-short">Plano</span>
            </button>
          </div>
        </div>
      </nav>

      {tab === "jornada" ? (
        <main id="panel" role="tabpanel" aria-labelledby="tab-jornada">
          <Hero kpis={data.kpis} plan={data.plan} activities={data.activities} onOpenPlan={openPlan} />
          <RecentActivities activities={data.activities} />
          <RunningSection kpis={data.kpis} weeks={data.weekly} activities={data.activities} />
          <StrengthSection kpis={data.kpis} />
          <HistorySection monthly={data.monthly} quarters={data.quarterly} activities={data.activities} />
        </main>
      ) : (
        <main id="panel" role="tabpanel" aria-labelledby="tab-plano">
          {/* O plano vem primeiro; os perfis dos coaches mudam pouco e ficam no fim. */}
          <section className="block wrap">
            <WeeklyPlan plan={data.plan} />
            <CoachProfiles coaches={data.coaches} />
          </section>
        </main>
      )}

      <footer>
        <div className="wrap">
          <p>
            Dados reais do <a href="https://www.strava.com/" target="_blank" rel="noopener">Strava</a>,
            atualizados diariamente ·{" "}
            <a href="https://github.com/ElderGil/RunForrestRun" target="_blank" rel="noopener">código aberto</a>
          </p>
          <p className="updated">Atualizado em {fmtDate(data.kpis.generated_at)}</p>
        </div>
      </footer>
    </>
  );
}
