import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/services/api";

export default function ReportsPageV2() {
  const today = new Date().toISOString().split("T")[0];
  const [selectedDate, setSelectedDate] = useState(today);

  const { data: reports = [], isLoading } = useQuery({
    queryKey: ["reports-v2", selectedDate],
    queryFn: async () => {
      const res = await api.get("/daily-reports/", {
        params: { report_date: selectedDate },
      });
      return res.data;
    },
    refetchInterval: 60000,
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">
          Daily Monitoring Reports
        </h1>

        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="border rounded-lg px-3 py-2"
        />
      </div>

      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <div className="bg-white border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3 text-left">Office</th>
                <th className="p-3 text-center">SB</th>
                <th className="p-3 text-center">PLI</th>
                <th className="p-3 text-center">Premium</th>
              </tr>
            </thead>

            <tbody>
              {reports.map((r: any) => (
                <tr key={`${r.office_id}-${r.report_date}`} className="border-t">
                  <td className="p-3">{r.office_name}</td>
                  <td className="p-3 text-center">{r.net_accounts}</td>
                  <td className="p-3 text-center">{r.pli_policies}</td>
                  <td className="p-3 text-center">{r.premium}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
