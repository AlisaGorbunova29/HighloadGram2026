import { useState } from "react";
import { api } from "../api";
import type { Channel } from "../types";

interface Props {
  channels: Channel[];
  userId: number;
  onSelect: (ch: Channel) => void;
  onRefresh: () => void;
}

export default function Channels({ channels, userId, onSelect, onRefresh }: Props) {
  const [newName, setNewName] = useState("");

  const create = async () => {
    if (!newName) return;
    await api.createChannel(newName, userId);
    setNewName("");
    onRefresh();
  };

  const subscribe = async (id: number) => {
    await api.subscribe(id, userId);
    alert("Подписка оформлена");
  };

  return (
    <div>
      <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Новый канал"
          style={{ flex: 1 }}
        />
        <button onClick={create}>+</button>
      </div>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {channels.map((ch) => (
          <li key={ch.id} style={{ marginBottom: 4, display: "flex", gap: 4 }}>
            <button onClick={() => onSelect(ch)} style={{ flex: 1, textAlign: "left" }}>
              {ch.name}
            </button>
            <button onClick={() => subscribe(ch.id)}>Подписаться</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
