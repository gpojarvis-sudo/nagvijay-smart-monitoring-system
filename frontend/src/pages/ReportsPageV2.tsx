import { useState } from "react";
import { todayIST } from "@/utils/date";
import { useQuery } from "@tanstack/react-query";
import api from "@/services/api";

export default function ReportsPageV2() {
  const today = todayIST();
  const [selectedDate, setSelectedDate] = useState(today);
  const [search, setSearch] = useState("");

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


  const reportingCount = reports.length;

  const totalOffices = 66;

  const pendingCount = totalOffices - reportingCount;

  const exportReport = (format:"excel"|"csv")=>{
    const base = (import.meta.env.VITE_API_URL || "https://nagvijay-smart-monitoring-system.onrender.com").replace(/\/$/, "");
    const token = localStorage.getItem("access_token");
    window.open(
      `${base}/api/v1/daily-reports/export?report_date=${selectedDate}&format=${format}&token=${encodeURIComponent(token || "")}`,
      "_blank"
    );
  };

  const filteredReports = reports.filter((r:any)=>
    (r.office_name || "").toLowerCase().includes(search.toLowerCase())
  );

  return (

    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">
          Daily Monitoring Reports
        </h1>

        <div className="flex gap-3">

          <input
            type="text"
            placeholder="Search office..."
            value={search}
            onChange={(e)=>setSearch(e.target.value)}
            className="border rounded-lg px-3 py-2 w-64"
          />

          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border rounded-lg px-3 py-2"
          />
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => exportReport("excel")}
            className="bg-green-600 text-white px-4 py-2 rounded-lg"
          >
            Excel
          </button>

          <button
            onClick={() => exportReport("csv")}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg"
          >
            CSV
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="bg-blue-50 border rounded-xl p-5">
          <p className="text-sm text-gray-600">Total Offices</p>
          <h2 className="text-3xl font-bold">66</h2>
        </div>

        <div className="bg-green-50 border rounded-xl p-5">
          <p className="text-sm text-gray-600">Reporting Offices</p>
          <h2 className="text-3xl font-bold text-green-700">{reportingCount}</h2>
        </div>

        <div className="bg-red-50 border rounded-xl p-5">
          <p className="text-sm text-gray-600">Pending Offices</p>
          <h2 className="text-3xl font-bold text-red-700">{pendingCount}</h2>
        </div>

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
              {filteredReports.map((r: any) => (
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
