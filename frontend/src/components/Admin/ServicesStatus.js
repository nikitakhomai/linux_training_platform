import React, { useState, useEffect } from "react";

const ServicesStatus = () => {
  const [services, setServices] = useState([
    { name: "Auth Service", port: 8000, status: "checking" },
    { name: "Task Service", port: 8001, status: "checking" },
    { name: "Check Service", port: 8002, status: "checking" },
    { name: "Orchestration Service", port: 8003, status: "checking" },
    { name: "Progress Service", port: 8004, status: "checking" },
  ]);

  const checkHealth = async (port) => {
    try {
      const response = await fetch(`http://localhost:${port}/health`);
      return response.ok ? "online" : "degraded";
    } catch {
      return "offline";
    }
  };

  useEffect(() => {
    const checkServices = async () => {
      const updated = await Promise.all(
        services.map(async (service) => {
          const status = await checkHealth(service.port);
          return { ...service, status };
        }),
      );
      setServices(updated);
    };
    checkServices();
    const interval = setInterval(checkServices, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h3> System Status</h3>
      <div className="services-grid">
        {services.map((service) => (
          <div key={service.port} className="service-card">
            <h3>{service.name}</h3>
            <div className={`service-status status-${service.status}`}>
              {service.status === "online"
                ? "✅ Online"
                : service.status === "degraded"
                  ? "⚠️ Degraded"
                  : "❌ Offline"}
            </div>
            <div>Port: {service.port}</div>
            <a
              href={`http://localhost:${service.port}/docs`}
              target="_blank"
              rel="noopener noreferrer"
            >
              API Docs
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ServicesStatus;
