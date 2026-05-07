import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

const WebTerminal = ({ containerId, onClose }) => {
    const terminalRef = useRef(null);
    const terminal = useRef(null);
    const fitAddon = useRef(null);
    const ws = useRef(null);
    let inputBuffer = '';

    useEffect(() => {
        terminal.current = new Terminal({
            cursorBlink: true,
            fontSize: 14,
            fontFamily: 'Consolas, "Courier New", monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#aeafad'
            }
        });

        fitAddon.current = new FitAddon();
        terminal.current.loadAddon(fitAddon.current);
        terminal.current.open(terminalRef.current);
        fitAddon.current.fit();

        const wsUrl = `ws://localhost:8003/api/v1/containers/ws/${containerId}`;
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            terminal.current.write('\x1b[32m✅ Connected!\r\n');
            terminal.current.write('\x1b[33mType commands and press Enter:\r\n');
            terminal.current.write('\x1b[36m$ \x1b[0m');
        };

        // В WebTerminal.jsx, измени onData:
        terminal.current.onData((data) => {
            if (data === '\r') { // Enter
                if (inputBuffer.length > 0) {
                    ws.current.send('cmd:' + inputBuffer);  // Отправляем команду
                    terminal.current.write('\r\n');
                }
                inputBuffer = '';
            } else if (data === '\x7f') { // Backspace
                if (inputBuffer.length > 0) {
                    inputBuffer = inputBuffer.slice(0, -1);
                    terminal.current.write('\b \b');
                }
            } else {
                inputBuffer += data;
                terminal.current.write(data);
            }
        });

        // Обработка сообщений
        ws.current.onmessage = (event) => {
            terminal.current.write(event.data);
        };

        ws.current.onerror = (error) => {
            terminal.current.write('\x1b[31m❌ Connection error\r\n\x1b[0m');
        };

        ws.current.onclose = () => {
            terminal.current.write('\x1b[33m⚠️ Disconnected\r\n\x1b[0m');
        };

        const handleResize = () => {
            fitAddon.current.fit();
        };
        window.addEventListener('resize', handleResize);

        return () => {
            if (ws.current) ws.current.close();
            if (terminal.current) terminal.current.dispose();
            window.removeEventListener('resize', handleResize);
        };
    }, [containerId]);

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 1000,
            backgroundColor: '#1e1e1e'
        }}>
            <div style={{
                background: '#333',
                padding: '8px 16px',
                color: 'white',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <span>🐚 Terminal: {containerId}</span>
                <button onClick={onClose} style={{
                    background: '#d32f2f',
                    color: 'white',
                    border: 'none',
                    padding: '4px 12px',
                    cursor: 'pointer',
                    borderRadius: '4px'
                }}>✕ Close</button>
            </div>
            <div ref={terminalRef} style={{ height: 'calc(100% - 40px)', padding: '8px' }} />
        </div>
    );
};

export default WebTerminal;
