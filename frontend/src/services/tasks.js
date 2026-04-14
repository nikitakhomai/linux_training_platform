import api from "./api";

export const tasksService = {
  getTasks: async (courseId = null) => {
    const url = courseId
      ? `/tasks/tasks?course_id=${courseId}`
      : "/tasks/tasks";
    const response = await api.get(url);
    return response.data;
  },

  getTask: async (taskId) => {
    const response = await api.get(`/tasks/tasks/${taskId}`);
    return response.data;
  },

  getCourses: async () => {
    const response = await api.get("/tasks/courses");
    return response.data;
  },

  submitValidation: async (taskId, containerId) => {
    const response = await api.post("/check/validate", {
      task_id: taskId,
      container_id: containerId,
      user_id: parseInt(localStorage.getItem("userId")),
    });
    return response.data;
  },
};
