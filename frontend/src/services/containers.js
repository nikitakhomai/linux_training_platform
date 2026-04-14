import api from "./api";

export const containersService = {
  createContainer: async (taskId) => {
    const response = await api.post("/orchestrate/containers", {
      task_id: taskId,
      user_id: parseInt(localStorage.getItem("userId")),
    });
    return response.data;
  },

  getContainer: async (containerId) => {
    const response = await api.get(`/orchestrate/containers/${containerId}`);
    return response.data;
  },

  deleteContainer: async (containerId) => {
    const response = await api.delete(`/orchestrate/containers/${containerId}`);
    return response.data;
  },

  listContainers: async () => {
    const response = await api.get("/orchestrate/containers");
    return response.data;
  },
};
