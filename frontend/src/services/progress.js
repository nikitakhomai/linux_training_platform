import api from "./api";

export const progressService = {
  getProgress: async (userId) => {
    const response = await api.get(`/progress/user/${userId}`);
    return response.data;
  },

  getSummary: async () => {
    const response = await api.get("/progress/summary");
    return response.data;
  },

  getLeaderboard: async (limit = 10) => {
    const response = await api.get(`/leaderboard/?limit=${limit}`);
    return response.data;
  },

  submitTask: async (taskId, score, passed) => {
    const response = await api.post("/progress/submit", {
      task_id: taskId,
      user_id: parseInt(localStorage.getItem("userId")),
      score,
      passed,
    });
    return response.data;
  },
};
