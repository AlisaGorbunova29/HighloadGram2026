import { useState, useEffect } from "react";
import { api } from "../api";
import type { AnalyticsData } from "../types";

interface Props {
  channelId: number;
}

export default function Analytics({ channelId }: Props) {
  const [period, setPeriod] = useState<"day" | "month">("day");
  const [data, setData] = useState<AnalyticsData[]>([]);

  useEffect(() => {
    api.getAnalytics(channelId, period).then((res) => setData(res.data));
  }, [channelId, period]);

  return (
    <div style={{ padding: 20 }}>
      <h3>Аналитика канала</h3>
      <div style={{ marginBottom: 12 }}>
        <button onClick={() => setPeriod("day")} disabled={period === "day"}>По дням</button>
        <button onClick={() => setPeriod("month")} disabled={period === "month"} style={{ marginLeft: 8 }}>По месяцам</button>
      </div>
      <table border={1} cellPadding={8} style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>Период</th>
            <th>Сообщений</th>
            <th>Активных пользователей</th>
            <th>Подписчиков</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.date}>
              <td>{row.date}</td>
              <td>{row.messages_count}</td>
              <td>{row.active_users}</td>
              <td>{row.subscribers_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
