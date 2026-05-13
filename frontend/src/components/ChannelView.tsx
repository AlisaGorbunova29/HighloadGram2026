import { useState, useEffect, useRef } from "react";
import { api } from "../api";
import type { Channel, Message, Tag } from "../types";

interface Props {
  channel: Channel;
  userId: number;
}

export default function ChannelView({ channel, userId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [content, setContent] = useState("");
  const [tagId, setTagId] = useState<number | undefined>();
  const [filterTagId, setFilterTagId] = useState<number | undefined>();
  const [newTag, setNewTag] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const isAdmin = userId === channel.admin_id;

  const load = async () => {
    const msgs = await api.listMessages(channel.id, filterTagId);
    setMessages(msgs);
  };

  useEffect(() => {
    load();
    api.listTags(channel.id).then(setTags);
  }, [channel.id, filterTagId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!content) return;
    await api.sendMessage(channel.id, userId, content, tagId);
    setContent("");
    load();
  };

  const createTag = async () => {
    if (!newTag) return;
    await api.createTag(channel.id, newTag, userId);
    setNewTag("");
    api.listTags(channel.id).then(setTags);
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
      <div style={{ padding: 8, borderBottom: "1px solid #eee" }}>
        <span>Теги: </span>
        <select value={filterTagId || ""} onChange={(e) => setFilterTagId(e.target.value ? Number(e.target.value) : undefined)}>
          <option value="">Все</option>
          {tags.map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        {isAdmin && (
          <>
            <input value={newTag} onChange={(e) => setNewTag(e.target.value)} placeholder="Новый тег" style={{ marginLeft: 8 }} />
            <button onClick={createTag}>+</button>
          </>
        )}
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: 12 }}>
        {messages.map((m) => (
          <div key={m.id} style={{ marginBottom: 8, padding: 8, background: "#f5f5f5", borderRadius: 4 }}>
            <small>{m.sender_name || "User #" + m.sender_id} · {new Date(m.created_at).toLocaleString()}</small>
            {m.primary_tag_name && <span style={{ marginLeft: 8, background: "#ddd", padding: "2px 6px", borderRadius: 4, fontSize: 12 }}>{m.primary_tag_name}</span>}
            <p style={{ margin: "4px 0 0" }}>{m.content}</p>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {isAdmin && (
        <div style={{ padding: 12, borderTop: "1px solid #ccc", display: "flex", gap: 8 }}>
          <select value={tagId || ""} onChange={(e) => setTagId(e.target.value ? Number(e.target.value) : undefined)}>
            <option value="">Без тега</option>
            {tags.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          <input
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Сообщение..."
            style={{ flex: 1 }}
          />
          <button onClick={send}>Отправить</button>
        </div>
      )}
    </div>
  );
}
