import React, { useState, useEffect } from 'react';
import { containersAPI } from '../../services/containers';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import WebTerminal from '../Terminal/WebTerminal';

const TaskModal = ({ task, onClose }) => {
    const [containerId, setContainerId] = useState(null);
    const [containerName, setContainerName] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showTerminal, setShowTerminal] = useState(false);
    const [isRestarting, setIsRestarting] = useState(false);
    const { user } = useAuth();

    // Проверка существования контейнера
    const checkContainerExists = async (id) => {
        try {
            const response = await fetch(`http://localhost:8003/api/v1/containers/${id}`, {
                headers: { 'X-User-ID': user.id.toString() }
            });
            return response.status === 200;
        } catch {
            return false;
        }
    };

    // Загружаем сохраненное состояние при монтировании
    useEffect(() => {
        const loadSavedContainer = async () => {
            console.log('TaskModal mounted for task:', task?.id);
            const saved = localStorage.getItem(`task_${task?.id}_state`);
            console.log('Saved state:', saved);
            
            if (saved) {
                try {
                    const data = JSON.parse(saved);
                    if (data.containerId && !data.isCompleted) {
                        // Проверяем, существует ли контейнер в Docker
                        const exists = await checkContainerExists(data.containerId);
                        if (exists) {
                            setContainerId(data.containerId);
                            setContainerName(data.containerName);
                            setResult(data.result || null);
                            toast.success('Reconnected to existing container');
                        } else {
                            // Контейнер не существует, очищаем сохранение
                            localStorage.removeItem(`task_${task?.id}_state`);
                            toast.error('Container expired. Please start a new one.');
                        }
                    }
                } catch (e) {
                    console.error('Failed to load saved state:', e);
                    localStorage.removeItem(`task_${task?.id}_state`);
                }
            }
        };
        
        loadSavedContainer();
    }, [task?.id, user.id]);

    // Сохраняем состояние
    useEffect(() => {
        if (containerId || result) {
            localStorage.setItem(`task_${task?.id}_state`, JSON.stringify({
                containerId,
                containerName,
                result,
                timestamp: Date.now()
            }));
        }
    }, [containerId, containerName, result, task?.id]);

    const startContainer = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8003/api/v1/containers/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-User-ID': user.id.toString(),
                    'X-User-Role': user.role
                },
                body: JSON.stringify({
                    task_id: task.id,
                    user_id: user.id,
                    docker_image: 'src-ssh-hardening-task:latest'
                })
            });
            const data = await response.json();
            setContainerId(data.container_id);
            setContainerName(data.name);
            toast.success('Container started!');
        } catch (error) {
            toast.error('Failed to start container');
        } finally {
            setLoading(false);
        }
    };

    const restartTask = async () => {
        setIsRestarting(true);
        try {
            // Удаляем старый контейнер, если есть
            if (containerId) {
                await fetch(`http://localhost:8003/api/v1/containers/${containerId}`, {
                    method: 'DELETE',
                    headers: { 'X-User-ID': user.id.toString() }
                });
            }
            // Очищаем состояние
            localStorage.removeItem(`task_${task.id}_state`);
            setContainerId(null);
            setContainerName(null);
            setResult(null);
            // Запускаем новый
            const response = await fetch('http://localhost:8003/api/v1/containers/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-User-ID': user.id.toString(),
                    'X-User-Role': user.role
                },
                body: JSON.stringify({
                    task_id: task.id,
                    user_id: user.id,
                    docker_image: 'src-ssh-hardening-task:latest'
                })
            });
            const data = await response.json();
            setContainerId(data.container_id);
            setContainerName(data.name);
            toast.success('Task restarted! New container created.');
        } catch (error) {
            toast.error('Failed to restart task');
        } finally {
            setIsRestarting(false);
        }
    };

    const validate = async () => {
        if (!containerId) {
            toast.error('Start container first');
            return;
        }
        
        // Проверяем, существует ли контейнер перед валидацией
        const exists = await checkContainerExists(containerId);
        if (!exists) {
            toast.error('Container expired. Please restart the task.');
            localStorage.removeItem(`task_${task.id}_state`);
            setContainerId(null);
            setContainerName(null);
            setResult(null);
            return;
        }
        
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8002/api/v1/validation/validate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-User-ID': user.id.toString(),
                    'X-User-Role': user.role
                },
                body: JSON.stringify({
                    task_id: task.id,
                    container_id: containerId,
                    user_id: user.id,
                    validation_type: 'ssh_config'
                })
            });
            const data = await response.json();
            setResult(data);
            if (data.status === 'passed') {
                toast.success(`✅ Validation passed! Score: ${data.total_score}%`);
            } else {
                toast.error(`❌ Validation failed! Score: ${data.total_score}%`);
            }
        } catch (error) {
            toast.error('Validation failed');
        } finally {
            setLoading(false);
        }
    };

    const completeTask = async () => {
        if (!containerId) {
            toast.error('Start container first');
            return;
        }
        
        // Проверяем существование контейнера
        const exists = await checkContainerExists(containerId);
        if (!exists) {
            toast.error('Container expired. Cannot complete task.');
            localStorage.removeItem(`task_${task.id}_state`);
            setContainerId(null);
            setContainerName(null);
            setResult(null);
            return;
        }
        
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8002/api/v1/validation/validate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-User-ID': user.id.toString(),
                    'X-User-Role': user.role
                },
                body: JSON.stringify({
                    task_id: task.id,
                    container_id: containerId,
                    user_id: user.id,
                    validation_type: 'ssh_config'
                })
            });
            const data = await response.json();
            
            if (data.status === 'passed') {
                await fetch('http://localhost:8004/api/v1/progress/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_id: task.id,
                        user_id: user.id,
                        score: data.total_score,
                        passed: true
                    })
                });
                
                toast.success(`🎉 Task completed! Score: ${data.total_score}%`);
                await containersAPI.delete(containerId);
                localStorage.removeItem(`task_${task.id}_state`);
                setTimeout(() => {
                    onClose();
                }, 1500);
            } else {
                toast.error(`Cannot complete: score ${data.total_score}% (need 80%)`);
            }
        } catch (error) {
            toast.error('Failed to complete task');
        } finally {
            setLoading(false);
        }
    };

    const openTerminal = () => {
        if (!containerId) {
            toast.error('Start container first');
            return;
        }
        setShowTerminal(true);
    };

    if (showTerminal) {
        return <WebTerminal containerId={containerId} onClose={() => setShowTerminal(false)} />;
    }

    return (
        <div className="modal active" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{task?.title}</h2>
                    <button className="close-btn" onClick={onClose}>✕</button>
                </div>
                <div className="requirements-list">
                    <strong>📋 Requirements:</strong>
                    <ul>
                        <li>Disable root login: <code>PermitRootLogin no</code></li>
                        <li>Disable password auth: <code>PasswordAuthentication no</code></li>
                        <li>Change SSH port: <code>Port 2222</code></li>
                        <li>Allow only student: <code>AllowUsers student</code></li>
                        <li>Limit attempts: <code>MaxAuthTries 3</code></li>
                    </ul>
                </div>
                
                {containerId && (
                    <div className="feedback success" style={{ marginBottom: 10 }}>
                        ✅ Container: {containerName}<br />
                        ID: {containerId}
                    </div>
                )}
                
                {result && (
                    <div className={`feedback ${result.status === 'passed' ? 'success' : 'error'}`}>
                        <strong>{result.status === 'passed' ? '✅ PASSED!' : '❌ FAILED!'}</strong>
                        <br />Score: {result.total_score}%
                        <br />{result.feedback}
                    </div>
                )}
                
                <div className="card-actions" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    {!containerId ? (
                        <button className="btn btn-primary" onClick={startContainer} disabled={loading}>
                            🚀 Start Container
                        </button>
                    ) : (
                        <>
                            <button className="btn btn-success" onClick={openTerminal} disabled={loading}>
                                💻 Open Terminal
                            </button>
                            <button className="btn btn-primary" onClick={validate} disabled={loading}>
                                ✅ Validate
                            </button>
                            <button className="btn btn-primary" onClick={completeTask} disabled={loading} style={{ background: '#10b981' }}>
                                🎉 Complete Task
                            </button>
                            <button className="btn btn-warning" onClick={restartTask} disabled={isRestarting} style={{ background: '#f59e0b', color: '#1e1e1e' }}>
                                🔄 Restart Task
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TaskModal;
