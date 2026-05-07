import { orchestrationClient } from "./api";

export const containersAPI = {
  create: (taskId, userId) =>
    orchestrationClient
      .post("/api/v1/containers/", {
        task_id: taskId,
        user_id: userId,
        docker_image: "src-ssh-hardening-task:latest",
      })
      .then((r) => r.data),

  list: () =>
    orchestrationClient.get("/api/v1/containers/").then((r) => r.data),

  get: (containerId) =>
    orchestrationClient
      .get(`/api/v1/containers/${containerId}`)
      .then((r) => r.data),

  delete: (containerId) =>
    orchestrationClient
      .delete(`/api/v1/containers/${containerId}`)
      .then((r) => r.data),

  getMetrics: (containerId) =>
    orchestrationClient
      .get(`/api/v1/containers/${containerId}/metrics`)
      .then((r) => r.data),

  list: () => orchestrationClient.get('/api/v1/containers/').then(r => r.data),
};
