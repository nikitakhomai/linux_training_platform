import React, { useState } from "react";
import ServicesStatus from "./ServicesStatus";
import CreateCourse from "./CreateCourse";
import CreateTask from "./CreateTask";

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState("services");

  return (
    <div className="admin-panel">
      <div className="tabs" style={{ marginBottom: 20 }}>
        <button
          className={`tab ${activeTab === "services" ? "active" : ""}`}
          onClick={() => setActiveTab("services")}
        >
          Services Status
        </button>
        <button
          className={`tab ${activeTab === "course" ? "active" : ""}`}
          onClick={() => setActiveTab("course")}
        >
          Create Course
        </button>
        <button
          className={`tab ${activeTab === "task" ? "active" : ""}`}
          onClick={() => setActiveTab("task")}
        >
          Create Task
        </button>
      </div>
      <div className="admin-content">
        {activeTab === "services" && <ServicesStatus />}
        {activeTab === "course" && <CreateCourse />}
        {activeTab === "task" && <CreateTask />}
      </div>
    </div>
  );
};

export default AdminPanel;
