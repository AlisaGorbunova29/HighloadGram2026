const API_BASE = "/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  createUser: (username: string) =>
    fetchJson<{ id: number }>("/users/", {
      method: "POST",
      body: JSON.stringify({ username }),
    }),

  listChannels: () => fetchJson<import("./types").Channel[]>("/channels/"),

  createChannel: (name: string, admin_id: number) =>
    fetchJson<import("./types").Channel>("/channels/", {
      method: "POST",
      body: JSON.stringify({ name, admin_id }),
    }),

  subscribe: (channelId: number, userId: number) =>
    fetchJson(`/channels/${channelId}/subscribe?user_id=${userId}`, { method: "POST" }),

  listTags: (channelId: number) =>
    fetchJson<import("./types").Tag[]>(`/channels/${channelId}/tags`),

  createTag: (channelId: number, name: string, userId: number) =>
    fetchJson<import("./types").Tag>(`/channels/${channelId}/tags?user_id=${userId}`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  listMessages: (channelId: number, tagId?: number, cursor?: string, limit = 20) => {
    const params = new URLSearchParams();
    params.set("limit", String(limit));
    if (tagId) params.set("tag_id", String(tagId));
    if (cursor) params.set("cursor", cursor);
    return fetchJson<import("./types").Message[]>(
      `/messages/channel/${channelId}?${params.toString()}`
    );
  },

  sendMessage: (channelId: number, senderId: number, content: string, tagId?: number) =>
    fetchJson<import("./types").Message>("/messages/", {
      method: "POST",
      body: JSON.stringify({
        channel_id: channelId,
        sender_id: senderId,
        content,
        primary_tag_id: tagId,
      }),
    }),

  getAnalytics: (channelId: number, period: "day" | "month", days = 30) =>
    fetchJson<{ data: import("./types").AnalyticsData[] }>(
      `/analytics/channel/${channelId}?period=${period}&days=${days}`
    ),
};
