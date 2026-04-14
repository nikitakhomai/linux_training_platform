import React, { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { WebLinksAddon } from "xterm-addon-web-links";
import "xterm/css/xterm.css";

const WebTerminal = ({ containerId, onClose }) => {
  const terminalRef = useRef(null);
  const terminal = useRef(null);
  const fitAddon = useRef(null);
  const ws = useRef(null);

  useEffect(() => {
    // Initialize terminal
    terminal.current = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: "monospace",
      theme: {
        background: "#1e1e1e",
        foreground: "#d4d4d4",
        cursor: "#aeafad",
      },
    });

    fitAddon.current = new FitAddon();
    terminal.current.loadAddon(fitAddon.current);
    terminal.current.loadAddon(new WebLinksAddon());

    terminal.current.open(terminalRef.current);
    fitAddon.current.fit();

    // Connect WebSocket
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws.current = new WebSocket(
      `${protocol}//${window.location.host}/orchestrate/ws/${containerId}`,
    );

    ws.current.onopen = () => {
      terminal.current.write("\x1b[32mConnected to container\x1b[0m\r\n");
    };

    ws.current.onmessage = (event) => {
      terminal.current.write(event.data);
    };

    ws.current.onerror = (error) => {
      terminal.current.write("\x1b[31mWebSocket error\x1b[0m\r\n");
    };

    ws.current.onclose = () => {
      terminal.current.write("\x1b[33mConnection closed\x1b[0m\r\n");
    };

    terminal.current.onData((data) => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(data);
      }
    });

    // Handle resize
    const handleResize = () => {
      fitAddon.current.fit();
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(
          JSON.stringify({
            type: "resize",
            cols: terminal.current.cols,
            rows: terminal.current.rows,
          }),
        );
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (terminal.current) {
        terminal.current.dispose();
      }
      window.removeEventListener("resize", handleResize);
    };
  }, [containerId]);

  return (
    <div className="terminal-container">
      <div className="terminal-header">
        <span>Container: {containerId}</span>
        <button onClick={onClose} className="close-btn">
          ✕
        </button>
      </div>
      <div ref={terminalRef} className="terminal" />
    </div>
  );
};

export default WebTerminal;
