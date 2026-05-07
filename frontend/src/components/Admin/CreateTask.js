import React, { useState, useEffect } from "react";
import { tasksAPI } from "../../services/tasks";
import toast from "react-hot-toast";

const CreateTask = () => {
  const [courses, setCourses] = useState([]);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    course_id: "",
    task_type: "ssh_config",
    points: 100,
    difficulty: "easy",
    docker_image: "src-ssh-hardening-task:latest",
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await tasksAPI.getCourses();
      setCourses(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to load courses:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const taskData = {
        title: formData.title,
        description: formData.description,
        task_type: formData.task_type,
        points: formData.points,
        difficulty: formData.difficulty,
        docker_image: formData.docker_image,
        is_published: true,
      };
      if (formData.course_id) taskData.course_id = parseInt(formData.course_id);

      await tasksAPI.createTask(taskData);
      toast.success("Task created successfully!");
      setFormData({
        title: "",
        description: "",
        course_id: "",
        task_type: "ssh_config",
        points: 100,
        difficulty: "easy",
        docker_image: "src-ssh-hardening-task:latest",
      });
    } catch (error) {
      toast.error("Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card">
      <h3> Create New Task</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Title</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
            required
          />
        </div>
        <div className="form-group">
          <label>Description</label>
          <textarea
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            rows="3"
          />
        </div>
        <div className="form-group">
          <label>Course</label>
          <select
            value={formData.course_id}
            onChange={(e) =>
              setFormData({ ...formData, course_id: e.target.value })
            }
          >
            <option value="">No course (standalone)</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.title}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Task Type</label>
          <select
            value={formData.task_type}
            onChange={(e) =>
              setFormData({ ...formData, task_type: e.target.value })
            }
          >
            <option value="ssh_config">SSH Configuration</option>
            <option value="file_permissions">File Permissions</option>
            <option value="firewall_rules">Firewall Rules</option>
          </select>
        </div>
        <div className="form-group">
          <label>Points</label>
          <input
            type="number"
            value={formData.points}
            onChange={(e) =>
              setFormData({ ...formData, points: parseInt(e.target.value) })
            }
          />
        </div>
        <div className="form-group">
          <label>Difficulty</label>
          <select
            value={formData.difficulty}
            onChange={(e) =>
              setFormData({ ...formData, difficulty: e.target.value })
            }
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
        <div className="form-group">
          <label>Docker Image</label>
          <input
            type="text"
            value={formData.docker_image}
            onChange={(e) =>
              setFormData({ ...formData, docker_image: e.target.value })
            }
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Creating..." : "Create Task"}
        </button>
      </form>
    </div>
  );
};

export default CreateTask;
