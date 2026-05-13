import { useState, useEffect } from "react";
import { api } from "./api";
import type { User, Channel } from "./types";
import Channels from "./components/Channels";
import ChannelView from "./components/ChannelView";
import Analytics from "./components/Analytics";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [view, setView] = useState<"chat" | "analytics">("chat");

  useEffect(() => {
    api.listChannels().then(setChannels);
  }, []);

  const handleLogin = async (username: string) => {
    const u = await api.createUser(username);
    setUser({ id: u.id, username, created_at: new Date().toISOString() });
  };

  if (!user) {
    return (
      <div style={{ maxWidth: 400, margin: "100px auto", textAlign: "center" }}>
        <h1>Messenger</h1>
        <input
          type="text"
          placeholder="Добро пожаловать! Введите имя пользователя"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleLogin((e.target as HTMLInputElement).value);
          }}
          style={{ padding: 8, width: "100%" }}
        />
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <aside style={{ width: 260, borderRight: "1px solid #ccc", padding: 12 }}>
        <h3>Каналы</h3>
        <Channels
          channels={channels}
          userId={user.id}
          onSelect={setSelectedChannel}
          onRefresh={() => api.listChannels().then(setChannels)}
        />
      </aside>

      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {selectedChannel ? (
          <>
            <div style={{ padding: 12, borderBottom: "1px solid #ccc", display: "flex", gap: 12 }}>
              <strong>{selectedChannel.name}</strong>
              <button onClick={() => setView("chat")}>Чат</button>
              <button onClick={() => setView("analytics")}>Аналитика</button>
            </div>
            {view === "chat" ? (
              <ChannelView channel={selectedChannel} userId={user.id} />
            ) : (
              <Analytics channelId={selectedChannel.id} />
            )}
          </>
        ) : (
          <div style={{ padding: 40 }}>Выберите канал</div>
        )}
      </main>
    </div>
  );
}
