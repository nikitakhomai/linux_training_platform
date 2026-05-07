import React from "react";

const TaskCard = ({
  task,
  onStart,
  onContinue,
  onDelete,
  showDelete,
  hasActiveContainer,
}) => {
  return (
    <div className="card">
      <div className="card-header">
        <h3>{task.title}</h3>
        <span className={`badge badge-${task.difficulty || "beginner"}`}>
          {task.difficulty || "beginner"}
        </span>
      </div>
      <div className="card-body">
        <p>{task.description || "Secure your Linux system"}</p>
        <p>🏆 {task.points || 100} points</p>
        <div className="card-actions">
          {hasActiveContainer ? (
            <button className="btn btn-success" onClick={onContinue}>
              ▶️ Continue
            </button>
          ) : (
            <button className="btn btn-primary" onClick={onStart}>
              🚀 Start Task
            </button>
          )}
          {showDelete && (
            <button className="btn btn-danger" onClick={onDelete}>
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskCard;
