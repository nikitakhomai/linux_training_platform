import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Проверяем доступность сервисов
    const checkServices = async () => {
      const servicesList = [
        { name: "Auth Service", url: "/auth/health" },
        { name: "Task Service", url: "/tasks/health" },
        { name: "Check Service", url: "/check/health" },
        { name: "Orchestration Service", url: "/orchestrate/health" },
        { name: "Progress Service", url: "/progress/health" },
      ];

      const results = await Promise.all(
        servicesList.map(async (service) => {
          try {
            const response = await fetch(service.url);
            if (response.ok) {
              return { ...service, status: "✅ Online", healthy: true };
            } else {
              return { ...service, status: "⚠️ Degraded", healthy: false };
            }
          } catch (error) {
            return { ...service, status: "❌ Offline", healthy: false };
          }
        }),
      );

      setServices(results);
      setLoading(false);
    };

    checkServices();
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>🐧 Linux Security Training Platform</h1>
        <p>Practice Linux security in isolated containers</p>
      </header>

      <main className="main">
        <div className="dashboard">
          <h2>System Status</h2>
          {loading ? (
            <p>Loading services status...</p>
          ) : (
            <div className="services-grid">
              {services.map((service, idx) => (
                <div key={idx} className="service-card">
                  <h3>{service.name}</h3>
                  <p
                    className={`status ${service.healthy ? "online" : "offline"}`}
                  >
                    {service.status}
                  </p>
                </div>
              ))}
            </div>
          )}

          <div className="info-section">
            <h2>Welcome to the Platform!</h2>
            <p>
              This is a hands-on Linux security training platform where you can:
            </p>
            <ul>
              <li>🔐 Learn security hardening techniques</li>
              <li>💻 Practice in isolated containers</li>
              <li>📊 Track your progress</li>
              <li>🏆 Compete on the leaderboard</li>
            </ul>
            <div className="coming-soon">
              <h3>🚀 Coming Soon</h3>
              <ul>
                <li>Interactive web terminal</li>
                <li>Task validation system</li>
                <li>Progress tracking</li>
                <li>Skill matrix visualization</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>
          Linux Security Training Platform v1.0 | Built for educational purposes
        </p>
      </footer>

      <style jsx>{`
        .app {
          font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
            Ubuntu, sans-serif;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #333;
        }

        .header {
          background: rgba(255, 255, 255, 0.95);
          padding: 2rem;
          text-align: center;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
          margin: 0;
          color: #667eea;
          font-size: 2rem;
        }

        .header p {
          margin: 0.5rem 0 0;
          color: #666;
        }

        .main {
          max-width: 1200px;
          margin: 2rem auto;
          padding: 0 1rem;
        }

        .dashboard {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        .services-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin: 1.5rem 0;
        }

        .service-card {
          padding: 1rem;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          text-align: center;
          background: #f9f9f9;
        }

        .service-card h3 {
          margin: 0 0 0.5rem;
          font-size: 1rem;
        }

        .status {
          font-weight: bold;
          margin: 0;
        }

        .status.online {
          color: #10b981;
        }

        .status.offline {
          color: #ef4444;
        }

        .info-section {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 2px solid #e0e0e0;
        }

        .info-section ul {
          list-style: none;
          padding: 0;
        }

        .info-section li {
          padding: 0.5rem 0;
          color: #555;
        }

        .coming-soon {
          background: #f0f9ff;
          padding: 1rem;
          border-radius: 8px;
          margin-top: 1rem;
        }

        .coming-soon h3 {
          color: #667eea;
          margin: 0 0 0.5rem;
        }

        .footer {
          background: rgba(255, 255, 255, 0.95);
          text-align: center;
          padding: 1rem;
          margin-top: 2rem;
          color: #666;
          font-size: 0.875rem;
        }
      `}</style>
    </div>
  );
}

export default App;
