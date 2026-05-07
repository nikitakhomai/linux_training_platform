import React, { useState, useEffect } from 'react';
import TaskCard from './TaskCard';
import TaskModal from './TaskModal';
import { tasksAPI } from '../../services/tasks';
import { containersAPI } from '../../services/containers';
import { useAuth } from '../../contexts/AuthContext';

const TaskList = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState(null);
    const [activeContainers, setActiveContainers] = useState({});
    const { user } = useAuth();

    useEffect(() => {
        loadTasks();
    }, []);

    useEffect(() => {
        if (tasks.length > 0) {
            loadActiveContainers();
        }
    }, [tasks]);

    const loadTasks = async () => {
        try {
            const data = await tasksAPI.getAll();
            setTasks(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('Failed to load tasks:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadActiveContainers = async () => {
        try {
            const containers = {};
            
            // Проверяем localStorage
            tasks.forEach(task => {
                const saved = localStorage.getItem(`task_${task.id}_state`);
                if (saved) {
                    try {
                        const state = JSON.parse(saved);
                        if (state.containerId) {
                            containers[task.id] = true;
                        }
                    } catch (e) {}
                }
            });
            
            // Проверяем активные контейнеры через API
            try {
                const data = await containersAPI.list();
                if (data.containers) {
                    data.containers.forEach(container => {
                        containers[container.task_id] = true;
                    });
                }
            } catch (error) {
                console.error('Failed to load containers from API:', error);
            }
            
            setActiveContainers(containers);
        } catch (error) {
            console.error('Failed to load containers:', error);
        }
    };

    const handleTaskAction = (task) => {
        setSelectedTask(task);
    };

    const handleClose = () => {
        setSelectedTask(null);
        loadActiveContainers();
    };

    const handleDelete = async (taskId) => {
        if (window.confirm('Delete this task?')) {
            await tasksAPI.deleteTask(taskId);
            await loadTasks();
            localStorage.removeItem(`task_${taskId}_state`);
        }
    };

    if (loading) return <div className="form-card">Loading tasks...</div>;
    if (tasks.length === 0) {
        return (
            <div className="form-card">
                <p>📭 No tasks available.</p>
                {(user?.role === 'admin' || user?.role === 'teacher') && <p>Click "Create Task" tab to add your first task!</p>}
            </div>
        );
    }

    return (
        <>
            <div className="tasks-grid">
                {tasks.map(task => (
                    <TaskCard 
                        key={task.id} 
                        task={task} 
                        onStart={() => handleTaskAction(task)}
                        onContinue={() => handleTaskAction(task)}
                        onDelete={() => handleDelete(task.id)} 
                        showDelete={user?.role === 'admin' || user?.role === 'teacher'}
                        hasActiveContainer={!!activeContainers[task.id]}
                    />
                ))}
            </div>
            {selectedTask && (
                <TaskModal 
                    task={selectedTask} 
                    onClose={handleClose}
                />
            )}
        </>
    );
};

export default TaskList;
